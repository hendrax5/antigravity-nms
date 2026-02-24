from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    """
    Detailed Audit Trail: 
    Log lengkap mengenai siapa yang melakukan perubahan konfigurasi, kapan, dan hasilnya (Success/Fail).
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # ID of user making the change
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    
    action = Column(String, nullable=False) # e.g., 'deploy_config', 'backup_config'
    status = Column(String, nullable=False) # 'success', 'fail'
    details = Column(JSON, nullable=True) # Store payload or error trace
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
