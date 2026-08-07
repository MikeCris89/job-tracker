from datetime import date, timedelta
import re

from sqlmodel import Session, select

from app.models import JobPosting, JobPostingCreate, Skill
from app.schemas import PostingExtraction

def normalize_slug(raw: str):
    s = raw.lower().strip()
    s = re.sub(r"\.(js|css|ts)$", "", s)   # strip framework suffixes
    s = re.sub(r"[\s.]+", "-", s)          # spaces and dots -> dash
    s = re.sub(r"[^a-z0-9+#-]", "", s)     # keep alnum, +, #, dash
    s = s.strip("-")                       # trim leading/trailing dashes
    return s

def get_or_create_skills(session: Session, names: list[str], *, in_stack: bool = False) -> list[Skill]:
    seen: dict[str, Skill] = {}
    for name in names:
        slug = normalize_slug(name)
        if slug in seen:
            continue
        skill = session.exec(select(Skill).where(Skill.slug == slug)).first()
        if skill is None:
            skill = Skill(slug=slug, name=name, in_my_stack=in_stack)
            session.add(skill)
            session.flush()
        elif in_stack and not skill.in_my_stack:
            skill.in_my_stack = True
        seen[slug] = skill
    return list(seen.values())

def _resolve_posted_date(extraction: PostingExtraction) -> date | None:
    if extraction.posted_date_stated is not None:
        return extraction.posted_date_stated
    if extraction.posting_age is not None:
        return date.today() - timedelta(days=extraction.posting_age)
    return None



def extraction_to_create(extraction: PostingExtraction, raw: str) -> JobPostingCreate:
    data = extraction.model_dump(exclude={"posting_age", "posted_date_stated"})
    data["posting_date"] = _resolve_posted_date(extraction)
    data["raw_posting"] = raw
    return JobPostingCreate(**data)

def posting_to_text(posting: JobPosting) -> str:
    parts = [
        f"Role: {posting.role}",
        f"Company: {posting.company}",
    ]
    # only include fields that exist — empty labels are noise the model has to ignore
    if posting.role_category:
        parts.append(f"Category: {posting.role_category}")
    if posting.years_experience is not None:
        parts.append(f"Years experience required: {posting.years_experience}")
    if posting.work_mode:
        parts.append(f"Work mode: {posting.work_mode}")
    if posting.summary:
        parts.append(f"\n{posting.summary}")
    return "\n".join(parts)