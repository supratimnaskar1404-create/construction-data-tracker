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
    awardee: Optional[str] = None
    award_value: Optional[float] = None
    awardee_contact_name: Optional[str] = None
    awardee_contact_email: Optional[str] = None
    awardee_contact_phone: Optional[str] = None

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
def read_tenders(skip: int = 0, limit: int = 5000, db: Session = Depends(get_db)):
    tenders = db.query(models.Tender).offset(skip).limit(limit).all()
    return tenders

@app.post("/api/reset-db")
def reset_database(db: Session = Depends(get_db)):
    try:
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        return {"message": "Database reset successfully. Schema updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape")
def trigger_scrape(agency: str, months_back: int = 0, db: Session = Depends(get_db)):
    agencies_to_scrape = []
    if agency.lower() == "all":
        agencies_to_scrape = ["eprocure", "nhai", "cpwd", "kpwd"]
    else:
        agencies_to_scrape = [agency.lower()]
        
    total_scraped = 0
    for ag in agencies_to_scrape:
        if ag == "eprocure":
            from .scrapers.eprocure import EProcureScraper
            scraper = EProcureScraper()
        elif ag == "nhai":
            from .scrapers.nhai import NHAIScraper
            scraper = NHAIScraper()
        elif ag == "cpwd":
            from .scrapers.cpwd import CPWDScraper
            scraper = CPWDScraper()
        elif ag == "kpwd":
            from .scrapers.kpwd import KPWDScraper
            scraper = KPWDScraper()
        else:
            continue
            
        try:
            if months_back > 0:
                tenders = scraper.scrape_awarded_tenders(months_back=months_back)
            else:
                tenders = scraper.scrape_active_tenders()
            
            # Save to DB
            seen_refs = set()
            for t in tenders:
                if t["reference_no"] in seen_refs:
                    continue
                seen_refs.add(t["reference_no"])
                
                existing = db.query(models.Tender).filter(models.Tender.reference_no == t["reference_no"]).first()
                if not existing:
                    db_tender = models.Tender(**t)
                    db.add(db_tender)
            db.commit()
            total_scraped += len(tenders)
        except Exception as e:
            print(f"Failed to scrape {ag}: {e}")
            
    return {"message": f"Scraped {total_scraped} tenders across {len(agencies_to_scrape)} agencies"}
