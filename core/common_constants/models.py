from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class TranscribedFile(Base):
    __tablename__ = "transcribed_files"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_location = Column(String, nullable=False, unique=True)
    date_transcribed = Column(DateTime(timezone=True))
    date_added = Column(DateTime(timezone=True))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    last_modified_date = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
