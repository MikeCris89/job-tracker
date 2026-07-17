import re

from sqlmodel import Session, select

from app.models import Skill

def normalize_slug(raw: str):
    s = raw.lower().strip()
    s = re.sub(r"\.(js|css|ts)$", "", s)   # strip framework suffixes
    s = re.sub(r"[\s.]+", "-", s)          # spaces and dots -> dash
    s = re.sub(r"[^a-z0-9+#-]", "", s)     # keep alnum, +, #, dash
    s = s.strip("-")                       # trim leading/trailing dashes
    return s

def get_or_create_skills(session: Session, names: list[str]) -> list[Skill]:
    seen: dict[str, Skill] = {}
    for name in names:
        slug = normalize_slug(name)
        if slug in seen:
            continue
        skill = session.exec(select(Skill).where(Skill.slug == slug)).first()
        if skill is None:
            skill = Skill(slug=slug, name=name, in_my_stack=False)
            session.add(skill)
            session.flush()
        seen[slug] = skill
    return list(seen.values())