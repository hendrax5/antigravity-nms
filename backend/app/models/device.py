from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    credential_id = Column(Integer, ForeignKey("credential_profiles.id"), nullable=True)
    
    hostname = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    vendor = Column(String, nullable=False) # e.g., cisco_ios, juniper_junos, mikrotik
    
    connection_method = Column(String, nullable=False, default="ssh") # ssh or snmp
    port = Column(Integer, nullable=False, default=22)
    snmp_community = Column(String, nullable=True)

    status = Column(String, default="active") # active, offline, maintenance

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    site = relationship("Site", backref="devices")
    credential = relationship("CredentialProfile", backref="devices")
