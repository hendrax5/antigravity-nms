from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.device import Device
from app.models.credential import CredentialProfile
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.network.tasks import execute_command, fetch_interfaces, configure_ip, configure_bgp, configure_policy, backup_config
from app.network.nornir_tasks import deploy_config_template_nornir
from celery.result import AsyncResult
from pydantic import BaseModel

router = APIRouter()

@router.post("/", response_model=DeviceResponse)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    from app.models.site import Site
    site = db.query(Site).filter(Site.id == device.site_id).first()
    if not site:
        raise HTTPException(status_code=400, detail="Site ID not found")

    device_dict = device.model_dump(exclude={"ssh_username", "ssh_password"})
    
    if device.connection_method == "ssh":
        if not device.ssh_username or not device.ssh_password:
             raise HTTPException(status_code=400, detail="SSH username and password are required for SSH connection")
        
        new_cred = CredentialProfile(
            tenant_id=site.tenant_id,
            name=f"Auto-{device.hostname}-SSH",
            username=device.ssh_username,
            encrypted_password=device.ssh_password
        )
        db.add(new_cred)
        db.flush() 
        device_dict["credential_id"] = new_cred.id
    elif device.connection_method == "snmp":
        if not device.snmp_community:
            raise HTTPException(status_code=400, detail="SNMP Community is required for SNMP connection")
        device_dict["credential_id"] = None
    else:
        raise HTTPException(status_code=400, detail="Invalid connection method")

    new_device = Device(**device_dict)
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/", response_model=List[DeviceResponse])
def get_devices(site_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Device)
    if site_id:
        query = query.filter(Device.site_id == site_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

class CommandRequest(BaseModel):
    command: str

class IPConfigRequest(BaseModel):
    interface: str
    ip_address: str
    subnet_mask: str

class BGPConfigRequest(BaseModel):
    local_as: str
    neighbor_ip: str
    remote_as: str

class PolicyConfigRequest(BaseModel):
    map_name: str
    action: str
    sequence: int
    match_prefix: str

class BulkDeployRequest(BaseModel):
    tenant_id: int
    device_ids: List[int]
    template_content: str
    dry_run: bool = False
    
@router.post("/{device_id}/execute")
def execute_device_command(device_id: int, request: CommandRequest, db: Session = Depends(get_db)):
    # Fetch device and credential
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    if not credential:
        raise HTTPException(status_code=400, detail="Device has no valid credential profile")

    # Dispatch to Celery
    task = execute_command.delay(
        host=device.ip_address,
        vendor=device.vendor,
        username=credential.username,
        password=credential.encrypted_password, # In a real app, this would be decrypted here
        command=request.command
    )
    
    return {"task_id": task.id, "message": "Command dispatched to background worker"}
    
@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result if task_result.ready() else None
    }
    return result

@router.post("/{device_id}/interfaces")
def get_device_interfaces(device_id: int, db: Session = Depends(get_db)):
    # Fetch device and credential
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    if not credential:
        raise HTTPException(status_code=400, detail="Device has no valid credential profile")

    # Dispatch to Celery to fetch structured interface data
    task = fetch_interfaces.delay(
        host=device.ip_address,
        vendor=device.vendor,
        username=credential.username,
        password=credential.encrypted_password 
    )
    
    return {"task_id": task.id, "message": "Fetching interfaces in background"}

@router.post("/{device_id}/configure/ip")
def configure_device_ip(device_id: int, request: IPConfigRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    
    task = configure_ip.delay(
        host=device.ip_address, vendor=device.vendor, username=credential.username, password=credential.encrypted_password,
        interface=request.interface, ip_address=request.ip_address, subnet_mask=request.subnet_mask
    )
    return {"task_id": task.id, "message": "IP Configuration sent to worker"}

@router.post("/{device_id}/configure/bgp")
def configure_device_bgp(device_id: int, request: BGPConfigRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    
    task = configure_bgp.delay(
        host=device.ip_address, vendor=device.vendor, username=credential.username, password=credential.encrypted_password,
        local_as=request.local_as, neighbor_ip=request.neighbor_ip, remote_as=request.remote_as
    )
    return {"task_id": task.id, "message": "BGP Configuration sent to worker"}

@router.post("/{device_id}/configure/policy")
def configure_device_policy(device_id: int, request: PolicyConfigRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    
    task = configure_policy.delay(
        host=device.ip_address, vendor=device.vendor, username=credential.username, password=credential.encrypted_password,
        map_name=request.map_name, action=request.action, sequence=request.sequence, match_prefix=request.match_prefix
    )
    return {"task_id": task.id, "message": "Routing Policy Configuration sent to worker"}

@router.post("/{device_id}/backup")
def backup_device_config(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    credential = db.query(CredentialProfile).filter(CredentialProfile.id == device.credential_id).first()
    if not credential:
        raise HTTPException(status_code=400, detail="Device has no valid credential profile")

    task = backup_config.delay(
        host=device.ip_address, vendor=device.vendor, username=credential.username, password=credential.encrypted_password, tenant_id=device.tenant_id
    )
    
    return {"task_id": task.id, "message": "Device configuration backup started"}

@router.post("/config/deploy")
def bulk_deploy_config(request: BulkDeployRequest, db: Session = Depends(get_db)):
    """
    Eksekusi konfigurasi ke banyak perangkat secara simultan dengan fitur Dry-run.
    Uses Nornir to run against all targeted inventory devices concurrently.
    """
    try:
        results = deploy_config_template_nornir(
            db=db,
            template_content=request.template_content,
            tenant_id=request.tenant_id,
            device_ids=request.device_ids,
            dry_run=request.dry_run
        )
        return {"message": "Bulk deployment successful", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.core.git_manager import GitManager
from app.models.tenant import Tenant

@router.get("/{device_id}/backup/history")
def get_device_backup_history(device_id: int, db: Session = Depends(get_db)):
    """
    Mengambil data riwayat konfigurasi dari Git.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    tenant = db.query(Tenant).filter(Tenant.id == device.tenant_id).first()
    if not tenant or not tenant.git_repo_url:
         raise HTTPException(status_code=400, detail="Tenant does not have a configured Git Repository")
         
    git_manager = GitManager(
        tenant_id=tenant.id, 
        repo_url=tenant.git_repo_url, 
        branch=tenant.git_branch, 
        token=tenant.git_token
    )
    
    history = git_manager.get_commit_history(hostname=device.ip_address)
    return {"device_id": device.id, "hostname": device.ip_address, "history": history}

@router.get("/{device_id}/backup/history/{commit_hash}")
def get_device_backup_content(device_id: int, commit_hash: str, db: Session = Depends(get_db)):
    """
    Mendapatkan isi konfigurasi spesifik pada titik commit Git tertentu.
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    tenant = db.query(Tenant).filter(Tenant.id == device.tenant_id).first()
    if not tenant or not tenant.git_repo_url:
         raise HTTPException(status_code=400, detail="Tenant does not have a configured Git Repository")
         
    git_manager = GitManager(
        tenant_id=tenant.id, 
        repo_url=tenant.git_repo_url, 
        branch=tenant.git_branch, 
        token=tenant.git_token
    )
    
    content = git_manager.get_file_content_at_commit(hostname=device.ip_address, commit_hash=commit_hash)
    if not content:
        raise HTTPException(status_code=404, detail="Configuration file not found for this commit")
        
    return {"device_id": device.id, "commit_hash": commit_hash, "content": content}

@router.get("/db/migrate")
def trigger_backend_migration():
    """
    Temporary endpoint to trigger database migration manually in Coolify since port 5432 is blocked.
    """
    import os
    import importlib.util
    try:
        migrate_path = os.path.join(os.path.dirname(__file__), "../../../migrate_db.py")
        spec = importlib.util.spec_from_file_location("migrate_db", migrate_path)
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)
        migrate_module.run_migration()
        return {"status": "Migration script executed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {e}")
