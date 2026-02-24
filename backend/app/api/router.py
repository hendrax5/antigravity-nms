from app.api.endpoints import tenant, site, credential, device, auth, monitoring, erp

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(erp.router, prefix="/erp", tags=["erp_integration"])
api_router.include_router(tenant.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(site.router, prefix="/sites", tags=["sites"])
api_router.include_router(credential.router, prefix="/credentials", tags=["credentials"])
api_router.include_router(device.router, prefix="/devices", tags=["devices"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
