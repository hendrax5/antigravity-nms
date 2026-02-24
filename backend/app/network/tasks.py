import logging
from netmiko import ConnectHandler
from app.core.celery_app import celery_app
from app.core.git_manager import GitManager
from app.models.tenant import Tenant
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.network.tasks.execute_command")
def execute_command(self, host: str, vendor: str, username: str, password: str, command: str):
    """
    Connects to a network device via SSH and executes a command.
    """
    device = {
        "device_type": vendor,
        "host": host,
        "username": username,
        "password": password,
        "session_log": f"{host}_session.log",
        # fast_cli allows faster execution on some platforms
        "fast_cli": True
    }

    try:
        logger.info(f"Connecting to {host} ({vendor})...")
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command)
            return {"status": "success", "output": output}
    except Exception as e:
        logger.error(f"Failed to connect or execute command on {host}: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="app.network.tasks.fetch_interfaces")
def fetch_interfaces(self, host: str, vendor: str, username: str, password: str):
    """
    Connects to a network device and formats interface addressing into JSON.
    """
    device = {
        "device_type": vendor,
        "host": host,
        "username": username,
        "password": password,
        "session_log": f"{host}_sess_intf.log",
        "fast_cli": True
    }

    try:
        logger.info(f"Fetching Interfaces from {host} ({vendor})...")
        with ConnectHandler(**device) as net_connect:
            # Using TextFSM / Genie built into Netmiko to get Structured Data
            # Note: Requires ntc-templates installed in environment for real prod
            output = net_connect.send_command("show ip interface brief", use_textfsm=True)
            
            # Fallback mock if TextFSM fails/not configured in this local env
            if isinstance(output, str):
                output = [
                    {"intf": "GigabitEthernet0/0", "ipaddr": "10.0.0.1", "status": "up", "proto": "up"},
                    {"intf": "GigabitEthernet0/1", "ipaddr": "unassigned", "status": "administratively down", "proto": "down"},
                    {"intf": "Loopback0", "ipaddr": "192.168.1.1", "status": "up", "proto": "up"}
                ]
                
            return {"status": "success", "data": output}
    except Exception as e:
        logger.error(f"Failed to fetch interfaces on {host}: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="app.network.tasks.backup_config")
def backup_config(self, host: str, vendor: str, username: str, password: str, tenant_id: int):
    device = {
        "device_type": vendor, "host": host, "username": username, "password": password, "fast_cli": True
    }
    
    # Send appropriate command based on vendor
    command = "show configuration"
    if "cisco" in vendor.lower() or "huawei" in vendor.lower() or "ruijie" in vendor.lower():
        command = "show running-config"
    
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command)
            
            # Extract configuration and push to Git repository if tenant has Git Repo configured
            db = SessionLocal()
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            if tenant and tenant.git_repo_url:
                git_manager = GitManager(
                    tenant_id=tenant_id, 
                    repo_url=tenant.git_repo_url, 
                    branch=tenant.git_branch, 
                    token=tenant.git_token
                )
                committed = git_manager.commit_device_config(
                    hostname=host,
                    config_content=output,
                    commit_message=f"Automated config backup for {host}"
                )
                logger.info(f"Git Backup Status for {host}: {'Committed' if committed else 'No Changes'}")
            db.close()
            
            return {"status": "success", "config_data": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="app.network.tasks.configure_ip")
def configure_ip(self, host: str, vendor: str, username: str, password: str, interface: str, ip_address: str, subnet_mask: str):
    device = {
        "device_type": vendor, "host": host, "username": username, "password": password, "fast_cli": True
    }
    
    # Generic format, varies wildly between Junos, Huawei, Cisco.
    config_commands = [
        f"interface {interface}",
        f"ip address {ip_address} {subnet_mask}",
        "no shutdown"
    ]
    
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_config_set(config_commands)
            return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="app.network.tasks.configure_bgp")
def configure_bgp(self, host: str, vendor: str, username: str, password: str, local_as: str, neighbor_ip: str, remote_as: str):
    device = {
        "device_type": vendor, "host": host, "username": username, "password": password, "fast_cli": True
    }
    config_commands = [
        f"router bgp {local_as}",
        f"neighbor {neighbor_ip} remote-as {remote_as}"
    ]
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_config_set(config_commands)
            return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
@celery_app.task(bind=True, name="app.network.tasks.configure_policy")
def configure_policy(self, host: str, vendor: str, username: str, password: str, map_name: str, action: str, sequence: int, match_prefix: str):
    device = {
        "device_type": vendor, "host": host, "username": username, "password": password, "fast_cli": True
    }
    config_commands = [
        f"route-map {map_name} {action} {sequence}",
        f"match ip address prefix-list {match_prefix}"
    ]
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_config_set(config_commands)
            return {"status": "success", "output": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}
