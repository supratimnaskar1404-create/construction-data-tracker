from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date
from typing import Optional

from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction Data Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContractSchema(BaseModel):
    id: int
    title: str
    value: Optional[float]
    location: Optional[str]
    award_date: Optional[date]
    source_url: Optional[str]
    agency: Optional[str]
    contractor_id: Optional[int]

    class Config:
        from_attributes = True

class ContractorSchema(BaseModel):
    id: int
    name: str
    location: Optional[str]
    verified: bool

    class Config:
        from_attributes = True

class TenderSchema(BaseModel):
    id: int
    title: str
    reference_no: str
    agency: str
    publishing_date: Optional[date]
    closing_date: Optional[date]
    source_url: Optional[str]
    status: str

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "Construction Data Tracker API is running"}

@app.get("/api/contracts", response_model=List[ContractSchema])
def get_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contracts = db.query(models.Contract).offset(skip).limit(limit).all()
    return contracts

@app.get("/api/contractors", response_model=List[ContractorSchema])
def get_contractors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contractors = db.query(models.Contractor).offset(skip).limit(limit).all()
    return contractors

@app.get("/api/tenders", response_model=List[TenderSchema])
def get_tenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tenders = db.query(models.Tender).offset(skip).limit(limit).all()
    return tenders

@app.post("/api/scrape")
def trigger_scrape(agency: str, db: Session = Depends(get_db)):
    if agency.lower() == "eprocure":
        from .scrapers.eprocure import EProcureScraper
        scraper = EProcureScraper()
        tenders = scraper.scrape_active_tenders()
        
        # Save to DB
        for t in tenders:
            existing = db.query(models.Tender).filter(models.Tender.reference_no == t["reference_no"]).first()
            if not existing:
                db_tender = models.Tender(**t)
                db.add(db_tender)
        db.commit()
        return {"message": f"Scraped {len(tenders)} tenders from {agency}"}
    
    return {"message": f"Scraping logic for {agency} not yet implemented"}
