from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
    name: Optional[str] = None

class TenantResponse(TenantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
