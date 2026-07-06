from datetime import datetime, timezone
from sqlmodel import Relationship, SQLModel, Field

class JobPostingSkillLink(SQLModel, table=True):
    posting_id: int | None = Field(default=None, foreign_key="jobposting.id" ,primary_key=True, ondelete="CASCADE")
    skill_id: int | None = Field(default=None, foreign_key="skill.id", primary_key=True, ondelete="CASCADE")

# Shared fields, the common shape. NOT a table.
class JobPostingBase(SQLModel):
    company: str
    role: str
    description: str
    job_type: str | None = None     # full-time, part-time, contract
    role_category: str | None = None
    status: str = "saved"
    location: str | None = None
    work_mode: str | None = None    # onsite/remote/hybrid
    source: str | None = None
    link: str | None = None
    date_applied: datetime | None = None
    follow_up_date: datetime | None = None
    years_experience: int | None = None
    contact: str | None = None
    notes: str | None = None
    match_score: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None    # annual/hourly
    raw_posting: str | None = None
    summary: str | None = None
   
# UPDATE WITH BASE
class JobPostingUpdate(SQLModel):
    company: str | None = None
    role: str | None = None
    description: str | None = None
    job_type: str | None = None 
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
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    raw_posting: str | None = None
    summary: str | None = None


# The table: base + the DB-only fields
class JobPosting(JobPostingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    skills: list["Skill"] = Relationship(
        back_populates="postings", link_model=JobPostingSkillLink
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Input shape: just the base, nothing added
class JobPostingCreate(JobPostingBase):
    pass


# Output shape: base + the fields we want to expose back
class JobPostingRead(JobPostingBase):
    id: int
    created_at: datetime

class Skill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True)
    name: str = Field(unique=True)
    in_my_stack: bool = False
    postings: list[JobPosting] = Relationship(
        back_populates="skills", link_model=JobPostingSkillLink
    )

