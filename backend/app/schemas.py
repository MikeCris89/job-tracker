from datetime import date

from sqlmodel import SQLModel, Field

class PostingExtraction(SQLModel):
    # required, always present in a real posting
    company: str
    role: str
    summary: str

    # extracted when present, null when not
    description: str | None = Field(
        default=None,
        description=(
            "What the company does and what the role's responsibilities are. "
            "Exclude the tech stack. Only state facts the posting explicitly "
            "provides. If the posting does not say what the company does, omit "
            "that entirely and describe only the responsibilities. Never infer "
            "or guess the company's business from its name or product names."
        ),
    )
    job_type: str | None = Field(
        default=None,
        description="One of exactly: full-time, part-time, contract. Lowercase."

    )
    role_category: str | None = Field(
        default=None,
        description=(
            "One of exactly: frontend, backend, fullstack. Lowercase. "
            "Base this on the actual work and requirements, not the job title. "
            "If the role requires meaningful work on both client and server, "
            "use fullstack even if the title says otherwise."
        ),
    )
    location: str | None = None
    work_mode: str | None = Field(
        default=None,
        description="One of exactly: onsite, remote, hybrid. Lowercase."
    )
    years_experience: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = Field(default=None, description="ISO currency code, e.g. CAD, USD.")
    salary_period: str | None = Field(default=None, description="One of exactly: annual, monthly, weekly, hourly. Use exactly what the posting states, do not convert.")
    source: str | None = Field(
        default=None,
        description=(
            "The job board or platform the posting was copied from, inferred from "
            "page furniture in the text (e.g. 'Easy Apply', 'X applicants' indicate "
            "LinkedIn). Not the aggregator or hiring company. Null if not obvious."
        ),
    )
    link: str | None = None
    contact: str | None = None
    posted_date_stated: date | None = Field(
        default=None,
        description="The publication date ONLY if the posting states an actual calendar date. Transcribe it, do not calculate it. Null if the posting only gives a relative age like '2 days ago'.",
    )
    posting_age: int | None = Field(
        default=None,
        description="Number of days since publication, as stated (e.g. '1 day ago' -> 1, '3 weeks ago' -> 21). Round down. Null if not stated.",
    )
    applicant_count: int | None = Field(
        default=None,
        description="number of applicants for posting if given. If the count is not provided put Null"
    )
    application_instructions: str | None = Field(
        default=None,
        description=(
            "Any special instruction for how to apply that goes beyond submitting "
            "a normal application: a code word or phrase to include, a specific "
            "subject line, a question to answer in the cover letter, a file naming "
            "convention, or an email address to apply to directly. Quote the "
            "instruction. Null if the posting has none."
        ),
    )

    # not a column, handled separately on save
    skills: list[str] = Field(
        default=[],
        description=(
            "Concrete technologies, languages, frameworks, and tools required or "
            "mentioned. Not soft skills, not years of experience, not methodologies "
            "like Agile. Write each one exactly as its own vendor or project writes "
            "it: 'TypeScript', 'PostgreSQL', 'AWS', 'C#', '.NET', 'HTML'. If the "
            "posting uses informal shorthand, correct it to the official name."
        ),
    )

class IngestRequest(SQLModel):
    raw_posting: str