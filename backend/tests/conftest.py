import os
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.config.database import Base, engine, get_db
from src.database import models
from datetime import datetime, timedelta
import uuid

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables once for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        cleanup_db = TestingSessionLocal()
        try:
            for table in reversed(Base.metadata.sorted_tables):
                cleanup_db.execute(table.delete())
            cleanup_db.commit()
        finally:
            cleanup_db.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency."""
    from app.main import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from src.utils.security import hash_password
    user = models.User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        name="Test User",
        role=models.UserRole.ORG_OWNER,
        phone="1234567890",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    from src.utils.security import hash_password
    admin = models.User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        name="Admin User",
        role=models.UserRole.ADMIN,
        phone="9999999999",
        password_hash=hash_password("admin123")
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_organization(db_session, test_user):
    """Create a test organization."""
    org = models.Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        email="org@example.com",
        phone="1234567890",
        address="123 Test St",
        city="Test City",
        state="Test State",
        pincode="12345",
        owner_id=test_user.id,
        subscription_status=models.SubscriptionStatus.ACTIVE,
        subscription_plan="basic",
        subscription_start=datetime.now(),
        subscription_end=datetime.now() + timedelta(days=30)
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    
    test_user.org_id = org.id
    db_session.commit()
    db_session.refresh(test_user)
    
    return org


@pytest.fixture
def test_client(db_session, test_organization):
    """Create a test client."""
    client = models.Client(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Client",
        email="client@example.com",
        phone="1234567890",
        address="456 Client St"
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def test_project(db_session, test_organization, test_client):
    """Create a test project."""
    project = models.Project(
        id=str(uuid.uuid4()),
        org_id=test_organization.id,
        name="Test Project",
        description="Test project description",
        status=models.ProjectStatus.IN_PROGRESS,
        client_id=test_client.id,
        budget=10000.0,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_token(db_session, test_user):
    """Create a test token."""
    token = models.Token(
        token="test_token_123",
        user_id=test_user.id,
        expires_at=datetime.now() + timedelta(days=1)
    )
    db_session.add(token)
    db_session.commit()
    return token
