from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.common_constants.constants import (
    DB_TYPE,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_PATH,
)
from core.common_constants.models import Base


def get_engine():
    """Create and return a SQLAlchemy engine based on DB_TYPE."""
    if DB_TYPE.lower() == "postgres":
        connection_string = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        print(f"Using PostgreSQL database: {DB_NAME}")

    elif DB_TYPE.lower() == "sqlite":
        db_path = Path(DB_PATH)

        # ✅ THIS is the missing line
        db_path.parent.mkdir(parents=True, exist_ok=True)

        connection_string = f"sqlite:///{db_path}"
        print(f"Using SQLite database: {db_path}")

    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}. Use 'sqlite' or 'postgres'")

    return create_engine(connection_string, pool_pre_ping=True)


def get_session():
    """Create and return a SQLAlchemy session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize the database by creating all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
