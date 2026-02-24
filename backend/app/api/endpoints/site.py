from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteResponse, SiteUpdate

router = APIRouter()

@router.post("/", response_model=SiteResponse)
def create_site(site: SiteCreate, db: Session = Depends(get_db)):
    new_site = Site(**site.model_dump())
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site

@router.get("/", response_model=List[SiteResponse])
def get_sites(tenant_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Site)
    if tenant_id:
        query = query.filter(Site.tenant_id == tenant_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{site_id}", response_model=SiteResponse)
def get_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site
