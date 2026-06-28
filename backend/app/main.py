from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models import JobPosting # noqa: F401
from app.database import create_db_and_tables 

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
def read_root():
    return {"message": "Job tracker API running."}

