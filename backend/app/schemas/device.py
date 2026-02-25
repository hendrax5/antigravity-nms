from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    hostname: str
    ip_address: str
    vendor: str
    site_id: int
    credential_id: Optional[int] = None
    connection_method: str = "ssh"
    port: int = 22
    snmp_community: Optional[str] = None

class DeviceCreate(DeviceBase):
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None

class DeviceUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    vendor: Optional[str] = None
    site_id: Optional[int] = None
    credential_id: Optional[int] = None
    connection_method: Optional[str] = None
    port: Optional[int] = None
    snmp_community: Optional[str] = None
    status: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
