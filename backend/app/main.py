from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select

from app.models import JobPosting, JobPostingCreate, JobPostingRead 
from app.database import create_db_and_tables, get_session 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
def read_root():
    return {"message": "Job tracker API running."}

@app.get("/postings", response_model=list[JobPostingRead])
def list_postings(session: Session = Depends(get_session)):
    postings = session.exec(select(JobPosting)).all()
    return postings

@app.post("/postings", response_model=JobPostingRead)
def create_posting(posting: JobPostingCreate, session: Session = Depends(get_session)):
    db_posting = JobPosting.model_validate(posting)
    session.add(db_posting)
    session.commit()
    session.refresh(db_posting)
    return db_posting

