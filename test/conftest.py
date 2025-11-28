import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base

@pytest.fixture(scope = 'session')
def engine():
    # Create an in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    
@pytest.fixture(scope = 'function')
def db_session(engine, monkeypatch):
    connection = engine.connect()
    transaction = connection.begin()
    
    TestSession = sessionmaker(bind = connection)
    session = TestSession()
    monkeypatch.setattr('app.database.get_session', lambda: session)
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()