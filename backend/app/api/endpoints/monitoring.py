from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.device import Device
from app.network.telegraf_config import generate_telegraf_config
from app.network.nornir_tasks import deploy_config_template_nornir
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class FastNetMonAlert(BaseModel):
    client_ip: str
    attack_type: str
    attack_severity: str
    tenant_id: int 

@router.post("/rebuild-telegraf")
def rebuild_telegraf_config(db: Session = Depends(get_db)):
    """
    Regenerates the telegraf.conf file based on the active device inventory.
    """
    success = generate_telegraf_config(db)
    if success:
        return {"message": "Telegraf configuration rebuilt successfully."}
    raise HTTPException(status_code=500, detail="Failed to rebuild Telegraf configuration.")

@router.post("/anomaly-webhook")
def fastnetmon_anomaly_webhook(alert: FastNetMonAlert, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Webhook endpoint to receive anomaly alerts from FastNetMon (or similar systems).
    Triggers an automated BGP Blackhole mitigation script if severity is high.
    """
    logger.warning(f"ANOMALY DETECTED: {alert.attack_type} on {alert.client_ip} (Tenant {alert.tenant_id})")
    
    # Example Mitigation Logic: Auto-BGP Blackhole
    # Find the core router for this tenant to inject the blackhole route
    devices = db.query(Device).filter(Device.tenant_id == alert.tenant_id, Device.hostname.ilike("%CORE%")).all()
    
    if not devices:
        logger.error(f"No Core routers found for Tenant {alert.tenant_id} to apply mitigation.")
        return {"status": "alert_received", "mitigation": "failed - no core router"}
        
    device_ids = [d.id for d in devices]
    
    # Jinja2 Template for BGP Blackholing (Cisco syntax example)
    blackhole_template = f"""
    ! BGP Blackhole Mitigation for {alert.client_ip}
    ip route {alert.client_ip} 255.255.255.255 Null0 tag 666
    router bgp 65000
     address-family ipv4
      network {alert.client_ip} mask 255.255.255.255 route-map RM-BLACKHOLE
    """
    
    # Dispatch Nornir task to the background to push the mitigation config
    background_tasks.add_task(
        deploy_config_template_nornir,
        db=db,
        template_content=blackhole_template,
        tenant_id=alert.tenant_id,
        device_ids=device_ids,
        dry_run=False
    )
    
    return {"status": "alert_received", "message": f"Auto-mitigation initiated for {alert.client_ip}"}
