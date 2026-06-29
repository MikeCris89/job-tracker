from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select

from app.models import JobPosting, JobPostingCreate, JobPostingRead, JobPostingUpdate 
from app.database import create_db_and_tables, get_session 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
def read_root():
    return {"message": "Job tracker API running."}


@app.post("/postings", response_model=JobPostingRead)
def create_posting(posting: JobPostingCreate, session: Session = Depends(get_session)):
    db_posting = JobPosting.model_validate(posting)
    session.add(db_posting)
    session.commit()
    session.refresh(db_posting)
    return db_posting

@app.patch("/postings/{posting_id}", response_model=JobPostingRead)
def update_posting(posting_id: int, posting_update: JobPostingUpdate, session: Session = Depends(get_session)):
    posting = session.get(JobPosting, posting_id)
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    update_data = posting_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(posting, key, value)

    session.add(posting)
    session.commit()
    session.refresh(posting)
    return posting

@app.get("/postings", response_model=list[JobPostingRead])
def list_postings(session: Session = Depends(get_session)):
    postings = session.exec(select(JobPosting)).all()
    return postings

@app.get("/postings/{posting_id}", response_model=JobPostingRead)
def get_posting(posting_id: int, session: Session = Depends(get_session)):
    posting = session.get(JobPosting, posting_id)
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    return posting

@app.delete("/postings/{posting_id}")
def delete_posting(posting_id: int, session: Session = Depends(get_session)):
    posting = session.get(JobPosting, posting_id)
    if not posting:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(posting)
    session.commit()
    return {"ok": True}