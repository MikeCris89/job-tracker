import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database import get_session

TEST_DATABASE_URL = "postgresql://jobtracker:localdevpassword@localhost:5433/jobtracker_test"

test_engine = create_engine(TEST_DATABASE_URL)

def get_test_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def client():
    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()