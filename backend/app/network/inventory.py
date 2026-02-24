from nornir.core.inventory import Inventory, Host, Group, Defaults
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.credential import CredentialProfile

class SQLAlchemyInventory:
    """
    Nornir Dynamic Inventory Plugin that fetches devices from the PostgreSQL database.
    """
    def __init__(self, db: Session, tenant_id: int = None, device_ids: list[int] = None):
        self.db = db
        self.tenant_id = tenant_id
        self.device_ids = device_ids

    def load(self) -> Inventory:
        hosts = {}
        
        # Build query
        query = self.db.query(Device, CredentialProfile).join(
            CredentialProfile, Device.credential_id == CredentialProfile.id
        )
        
        if self.tenant_id is not None:
            query = query.filter(Device.tenant_id == self.tenant_id)
            
        if self.device_ids:
            query = query.filter(Device.id.in_(self.device_ids))
            
        results = query.all()
        
        for device, credential in results:
            # Map DB vendor names to Nornir platforms (Netmiko/NAPALM standard)
            platform = device.vendor.lower()
            if "cisco" in platform:
                platform = "ios"
            elif "juniper" in platform:
                platform = "junos"
            elif "huawei" in platform:
                platform = "huawei"
                
            hosts[device.hostname] = Host(
                name=device.hostname,
                hostname=device.ip_address,
                username=credential.username,
                password=credential.encrypted_password,
                platform=platform,
                data={
                    "site_id": device.site_id,
                    "tenant_id": device.tenant_id,
                    "device_id": device.id,
                }
            )
            
        return Inventory(hosts=hosts, groups={}, defaults=Defaults())
