from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate

router = APIRouter()

@router.post("/", response_model=TenantResponse)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    db_tenant = db.query(Tenant).filter(Tenant.name == tenant.name).first()
    if db_tenant:
        raise HTTPException(status_code=400, detail="Tenant already exists")
    
    new_tenant = Tenant(**tenant.model_dump())
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    return new_tenant

@router.get("/", response_model=List[TenantResponse])
def get_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Tenant).offset(skip).limit(limit).all()

@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
