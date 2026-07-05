# display names only, slug is derived
from sqlmodel import Session, select

from app.models import Skill
from app.skills import normalize_slug
from app.database import engine


MY_STACK = [
    "React",
    "TypeScript",
    "JavaScript",
    "Next.js",
    "Redux Toolkit",
    "RTK Query",
    "TanStack Query",
    "Tailwind CSS",
    "Node.js",
    "Express",
    "PostgreSQL",
    "Prisma",
    "Firebase",
    "HTML",
    "CSS",
]

def seed_stack():
    with Session(engine) as session:
        for name in MY_STACK:
            slug = normalize_slug(name)
            exists = session.exec(select(Skill).where(Skill.slug == slug)).first()
            if exists:
                continue
            session.add(Skill(slug=slug, name=name, in_my_stack=True))
        session.commit()

if __name__ == "__main__":
    seed_stack()