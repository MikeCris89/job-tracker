import pytest
from sqlmodel import select

from app.skills import get_or_create_skills, normalize_slug
from app.models import Skill


@pytest.mark.parametrize("raw, expected", [
    (".NET", "net"),
    ("C#", "c#"),
    ("Node.js", "node"),
    ("React.js", "react"),
    ("React", "react"),
    ("C++", "c++"),
])
def test_normalize_slug(raw, expected):
    assert normalize_slug(raw) == expected

def test_get_or_create_skills_dedupes_by_slug(session):
    skills = get_or_create_skills(session, ["React", "React.js"])
    assert len(skills) == 1
    assert skills[0].slug == "react"


def test_get_or_create_skills_reuses_existing(session):
    first = get_or_create_skills(session, ["Rust"])
    second = get_or_create_skills(session, ["Rust"])
    assert first[0].id == second[0].id


def test_get_or_create_skills_creates_when_absent(session):
    skills = get_or_create_skills(session, ["Rust"])
    assert skills[0].id is not None
    assert skills[0].slug == "rust"
    assert skills[0].in_my_stack is False


def test_get_or_create_skills_persists_to_db(session):
    get_or_create_skills(session, ["Rust"])
    found = session.exec(select(Skill).where(Skill.slug == "rust")).first()
    assert found is not None
    assert found.name == "Rust"