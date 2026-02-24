from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CredentialProfileBase(BaseModel):
    name: str
    username: str
    tenant_id: int

class CredentialProfileCreate(CredentialProfileBase):
    password: str

class CredentialProfileUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class CredentialProfileResponse(CredentialProfileBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
