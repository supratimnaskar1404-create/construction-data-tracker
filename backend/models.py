from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from .database import Base

class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String, index=True, nullable=True)
    verified = Column(Boolean, default=False)
    
    contracts = relationship("Contract", back_populates="contractor")

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    value = Column(Float, nullable=True)
    location = Column(String, index=True, nullable=True)
    award_date = Column(Date, nullable=True)
    source_url = Column(String, nullable=True)
    agency = Column(String, index=True, nullable=True)
    
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    contractor = relationship("Contractor", back_populates="contracts")

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    reference_no = Column(String, unique=True, index=True)
    agency = Column(String, index=True)
    publishing_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    source_url = Column(String, nullable=True)
    status = Column(String, default="Active")
