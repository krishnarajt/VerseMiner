from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common_constants.constants import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from models import Base


def get_engine():
    """Create and return a SQLAlchemy engine."""
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(connection_string, pool_pre_ping=True)
    return engine


def get_session():
    """Create and return a SQLAlchemy session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize the database by creating all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
