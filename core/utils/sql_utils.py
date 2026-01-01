from datetime import datetime
from sqlalchemy.exc import IntegrityError
from models import TranscribedFile
from sql_connector import get_session


class SQLUtils:
    @staticmethod
    def add_file(file_location, date_transcribed=None, date_added=None):
        """Add a new file to the database."""
        session = get_session()
        try:
            new_file = TranscribedFile(
                file_location=file_location,
                date_transcribed=date_transcribed or datetime.now(),
                date_added=date_added or datetime.now(),
            )
            session.add(new_file)
            session.commit()
            file_id = new_file.file_id
            session.close()
            return file_id
        except IntegrityError:
            session.rollback()
            session.close()
            return None

    @staticmethod
    def file_exists(file_location):
        """Check if a file already exists in the database."""
        session = get_session()
        exists = (
            session.query(TranscribedFile)
            .filter_by(file_location=file_location)
            .first()
            is not None
        )
        session.close()
        return exists

    @staticmethod
    def get_file(file_location):
        """Get a file record by location."""
        session = get_session()
        file_record = (
            session.query(TranscribedFile)
            .filter_by(file_location=file_location)
            .first()
        )
        session.close()
        return file_record

    @staticmethod
    def update_transcription_date(file_location, date_transcribed=None):
        """Update the transcription date for a file."""
        session = get_session()
        try:
            file_record = (
                session.query(TranscribedFile)
                .filter_by(file_location=file_location)
                .first()
            )
            if file_record:
                file_record.date_transcribed = date_transcribed or datetime.now()
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            session.rollback()
            session.close()
            raise e

    @staticmethod
    def get_all_files():
        """Get all file records."""
        session = get_session()
        files = session.query(TranscribedFile).all()
        session.close()
        return files

    @staticmethod
    def delete_file(file_location):
        """Delete a file record."""
        session = get_session()
        try:
            file_record = (
                session.query(TranscribedFile)
                .filter_by(file_location=file_location)
                .first()
            )
            if file_record:
                session.delete(file_record)
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            session.rollback()
            session.close()
            raise e
