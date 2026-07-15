from sqlmodel import SQLModel

class PostingExtraction(SQLModel):
    # required, always present in a real posting
    company: str
    role: str
    summary: str

    # extracted when present, null when not
    description: str | None = None
    job_type: str | None = None
    role_category: str | None = None
    location: str | None = None
    work_mode: str | None = None
    years_experience: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    source: str | None = None
    link: str | None = None
    contact: str | None = None

    # not a column, handled separately on save
    skills: list[str] = []