from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select

from app.models import CV, JobPosting, JobPostingCreate, JobPostingRead, JobPostingUpdate 
from app.database import create_db_and_tables, get_session
from app.ai import extract_cv_skills, extract_cv_text, extract_posting
from app.schemas import IngestRequest, PostingExtraction
from app.skills import extraction_to_create, get_or_create_skills 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
def read_root():
    return {"message": "Job tracker API running."}




# Single write path: skills is list[str] on input models but a Relationship on
# the table, so it must never reach setattr — convert names to rows here only.
def apply_posting_data(session: Session, posting: JobPosting, data: JobPostingCreate | JobPostingUpdate, *, partial: bool) -> JobPosting:
    payload = data.model_dump(exclude_unset=partial, exclude={"skills"})
    for key, value in payload.items():
        setattr(posting, key, value)
    if "skills" in data.model_fields_set:
        posting.skills = get_or_create_skills(session, data.skills or [])
    return posting


@app.post("/postings", response_model=JobPostingRead)
def create_posting(posting: JobPostingCreate, session: Session = Depends(get_session)):
    db_posting = apply_posting_data(session, JobPosting(company=posting.company, role=posting.role), posting, partial=False)
    session.add(db_posting)
    session.commit()
    session.refresh(db_posting)
    return db_posting

@app.post('/postings/ingest', response_model=JobPostingCreate)
def ingest_posting(payload: IngestRequest):
    extraction = extract_posting(payload.raw_posting)
    return extraction_to_create(extraction, payload.raw_posting)


@app.patch("/postings/{posting_id}", response_model=JobPostingRead)
def update_posting(posting_id: int, posting_update: JobPostingUpdate, session: Session = Depends(get_session)):
    posting = session.get(JobPosting, posting_id)
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    apply_posting_data(session, posting, posting_update, partial=True)
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

@app.put("/cv")
def upsert_cv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    raw = file.file.read()                       # sync read
    text = extract_cv_text(raw, file.content_type)
    skills = extract_cv_skills(text)

    cv = session.exec(select(CV)).first()        # singleton: first row or none
    if cv is None:
        cv = CV(original=text)
        session.add(cv)
    else:
        cv.original = text                       # replace, don't append

    get_or_create_skills(session, skills, in_stack=True)
    session.commit()
    session.refresh(cv)
    return {"id": cv.id, "skills_added": skills}