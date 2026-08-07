from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select

from app.models import CV, JobPosting, JobPostingCreate, JobPostingRead, JobPostingUpdate, Skill 
from app.database import get_session
from app.ai import extract_cv_skills, extract_cv_text, extract_posting, score_match
from app.schemas import IngestRequest
from app.skills import extraction_to_create, get_or_create_skills, posting_to_text 

@asynccontextmanager  # turns this generator into an async context manager,
                      # so FastAPI can run it as `async with lifespan(app):`
                      # (same setup/teardown pattern as `with Session(...)` in get_session)
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # Everything ABOVE the yield runs ONCE, when the app process boots,
    # before a single request is served. In dev (fastapi dev) this re-runs
    # on every file-save reload, because each reload is a fresh process.
    # create_db_and_tables()  # ensures tables exist. NOTE: being retired —
                            # Alembic owns the schema now, so this becomes a no-op we remove.

    yield  # hands control to the app. It serves requests for its whole
           # lifetime here. Execution pauses on this line until shutdown.

    # --- SHUTDOWN ---
    # Everything BELOW the yield runs ONCE, when the app is stopping.
    # Cleanup goes here (close pools, flush caches, etc). Empty for now.

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

@app.post("/postings/{posting_id}/match")
def match_posting(posting_id: int, session: Session = Depends(get_session)):
    posting = session.get(JobPosting, posting_id)
    if posting is None:
        raise HTTPException(status_code=404, detail="Posting not found")

    cv = session.exec(select(CV)).first()
    if cv is None:
        raise HTTPException(status_code=400, detail="No CV uploaded")
    
    skills = session.exec(select(Skill).where(Skill.in_my_stack == True)).all()

    result = score_match(cv.original, [s.name for s in skills], posting_to_text(posting))

    posting.match_score = result.match_score
    posting.match_reasoning = result.match_reasoning
    posting.match_scored_at = datetime.now(timezone.utc)

    session.add(posting)
    session.commit()
    session.refresh(posting)

    return posting