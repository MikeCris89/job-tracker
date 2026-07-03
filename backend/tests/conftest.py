import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database import get_session

TEST_DATABASE_URL = "postgresql://jobtracker:localdevpassword@localhost:5433/jobtracker_test"

test_engine = create_engine(TEST_DATABASE_URL)

@pytest.fixture
def session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def client(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()