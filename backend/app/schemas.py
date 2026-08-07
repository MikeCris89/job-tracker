from datetime import date

from sqlmodel import SQLModel, Field

SKILLS_DESCRIPTION = (
    "Concrete technologies, languages, frameworks, libraries, and tools. "
    "Not soft skills, not years of experience, not methodologies like Agile. "
    "Include every technology named in the text, including distinct sub-services "
    "of a larger platform (e.g. 'Firebase Cloud Messaging', 'AWS S3'); when in "
    "doubt, include it. "
    "Write each one using its canonical product name, exactly as its vendor or "
    "project brands it: 'TypeScript', 'PostgreSQL', 'AWS', 'C#', '.NET', 'HTML'. "
    "Correct informal shorthand to that name ('TS' -> 'TypeScript', 'postgres' "
    "-> 'PostgreSQL'). Strip descriptive category words that are not part of the "
    "brand name: 'Prisma ORM' -> 'Prisma', 'Express.js framework' -> 'Express'. "
    "But keep branded sub-service names whole: 'Firebase Storage' stays "
    "'Firebase Storage', not 'Firebase'. Never include version numbers: "
    "'Next.js 15' -> 'Next.js', 'Python 3.12' -> 'Python'."
)

class PostingExtraction(SQLModel):
    # required, always present in a real posting
    company: str
    role: str
    summary: str

    # extracted when present, null when not
    description: str | None = Field(
        default=None,
        description=(
            "Prose describing the role's responsibilities and duties. Exclude the "
            "tech stack. Write this whenever the posting describes the role at all. "
            "If the posting states what the company does, open with one sentence on "
            "that; if it does not, skip that sentence and write only the "
            "responsibilities. Do not infer the company's business from its name or "
            "product names. Null only if the posting says nothing about the role."
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
    salary_currency: str | None = Field(
        default=None, 
        description="ISO currency code, e.g. CAD, USD."
        )
    salary_period: str | None = Field(
        default=None, 
        description="One of exactly: annual, monthly, weekly, hourly. Use exactly what the posting states, do not convert."
        )
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
        description=SKILLS_DESCRIPTION,
    )

class IngestRequest(SQLModel):
    raw_posting: str

class CVExtraction(SQLModel):
    skills: list[str] = Field(description=SKILLS_DESCRIPTION)

class MatchExtraction(SQLModel):
    match_score: int = Field(
        description=(
            "0-100. How well this candidate fits this specific posting. "
            "Weigh overlap between the candidate's actual demonstrated experience "
            "and what the posting requires. Treat a missing must-have requirement as "
            "a significant penalty; treat a missing nice-to-have as minor. "
            "Do not inflate: a score above 80 means the candidate is a strong, "
            "credible applicant for this exact role."
        )
    )
    match_reasoning: str = Field(
        description=(
            "2-4 sentences explaining the score. State the strongest points of "
            "alignment and the specific gaps that cost points. Reference concrete "
            "technologies and requirements, not generalities. Write it as advice to "
            "the candidate, not a description of them."
        )
    )