from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class JobPosting(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # core, always present
    company: str
    role: str
    role_category: str | None = None  
    description: str
    status: str = "saved"

    location: str | None = None
    work_mode: str | None = None          # remote / hybrid / onsite
    source: str | None = None             # LinkedIn, Adzuna, etc.
    link: str | None = None
    date_applied: datetime | None = None
    follow_up_date: datetime | None = None

    # your new ideas, good calls
    years_experience: int | None = None   # filter "<= 3 years"

    # free text, not for filtering
    contact: str | None = None
    notes: str | None = None

    # AI feature columns (unused for now)
    match_score: int | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))