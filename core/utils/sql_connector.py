from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from constants import DB_TYPE, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_PATH
from models import Base


def get_engine():
    """Create and return a SQLAlchemy engine based on DB_TYPE."""
    if DB_TYPE.lower() == "postgres":
        connection_string = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        print(f"Using PostgreSQL database: {DB_NAME}")
    elif DB_TYPE.lower() == "sqlite":
        connection_string = f"sqlite:///{DB_PATH}"
        print(f"Using SQLite database: {DB_PATH}")
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}. Use 'sqlite' or 'postgres'")

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
