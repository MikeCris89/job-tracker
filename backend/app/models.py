from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

# Shared fields, the common shape. NOT a table.
class JobPostingBase(SQLModel):
    company: str
    role: str
    description: str
    role_category: str | None = None
    status: str = "saved"
    location: str | None = None
    work_mode: str | None = None
    source: str | None = None
    link: str | None = None
    date_applied: datetime | None = None
    follow_up_date: datetime | None = None
    years_experience: int | None = None
    contact: str | None = None
    notes: str | None = None
    match_score: int | None = None

# UPDATE WITH BASE
class JobPostingUpdate(SQLModel):
    company: str | None = None
    role: str | None = None
    description: str | None = None
    role_category: str | None = None
    status: str | None = None
    location: str | None = None
    work_mode: str | None = None
    source: str | None = None
    link: str | None = None
    date_applied: datetime | None = None
    follow_up_date: datetime | None = None
    years_experience: int | None = None
    contact: str | None = None
    notes: str | None = None
    match_score: int | None = None


# The table: base + the DB-only fields
class JobPosting(JobPostingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Input shape: just the base, nothing added
class JobPostingCreate(JobPostingBase):
    pass


# Output shape: base + the fields we want to expose back
class JobPostingRead(JobPostingBase):
    id: int
    created_at: datetime