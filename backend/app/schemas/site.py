from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.tenant import TenantResponse

class SiteBase(BaseModel):
    name: str
    location: Optional[str] = None
    tenant_id: int

class SiteCreate(SiteBase):
    pass

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    tenant_id: Optional[int] = None

class SiteResponse(SiteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
