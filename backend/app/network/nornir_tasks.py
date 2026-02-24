import logging
from typing import Dict, Any, List
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_napalm.plugins.tasks import napalm_configure, napalm_get
from app.network.inventory import SQLAlchemyInventory
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

def get_nornir_object(db: Session, tenant_id: int = None, device_ids: list[int] = None):
    """
    Initializes a Nornir object dynamically using the SQLAlchemy inventory plugin.
    """
    inventory_plugin = SQLAlchemyInventory(db=db, tenant_id=tenant_id, device_ids=device_ids)
    
    # Init Nornir with memory inventory (since we provide the loaded inventory object directly)
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {"host_file": "", "group_file": "", "defaults_file": ""}
        }
    )
    
    # Overwrite the empty inventory with our dynamically loaded one
    nr.inventory = inventory_plugin.load()
    return nr

def deploy_config_template_nornir(db: Session, template_content: str, tenant_id: int, device_ids: list[int], dry_run: bool = False) -> Dict[str, Any]:
    """
    Deploys a rendered configuration text to multiple devices concurrently.
    Uses NAPALM where supported for safe atomic transactions, and Netmiko as fallback.
    """
    nr = get_nornir_object(db=db, tenant_id=tenant_id, device_ids=device_ids)
    
    def config_task(task):
        platform = task.host.platform
        
        # Example logic: Try NAPALM for Junos/IOS-XR, fallback to Netmiko for others
        if platform in ["junos", "iosxr", "eos"]:
            try:
                task.run(
                    task=napalm_configure,
                    configuration=template_content,
                    replace=False,
                    dry_run=dry_run
                )
            except Exception as e:
                task.host["error"] = str(e)
        else:
            # Fallback for standard Cisco IOS / Huawei using Netmiko Config Set
            if dry_run:
                task.host["error"] = "Dry-run not supported for platform via Netmiko. Skipping."
                return
                
            config_lines = template_content.splitlines()
            try:
                task.run(
                    task=netmiko_send_config,
                    config_commands=config_lines
                )
            except Exception as e:
                task.host["error"] = str(e)

    # Run the task concurrently across all filtered hosts
    result = nr.run(task=config_task)
    
    # Format the results for the API response
    response = []
    for host_name, task_result in result.items():
        is_failed = task_result.failed or "error" in nr.inventory.hosts[host_name].data
        response.append({
            "hostname": host_name,
            "ip": nr.inventory.hosts[host_name].hostname,
            "failed": is_failed,
            "result": task_result[0].result if not is_failed and task_result else str(task_result.exception) if task_result.exception else nr.inventory.hosts[host_name].data.get("error", "Unknown error")
        })
        
    return {"status": "completed", "dry_run": dry_run, "details": response}
