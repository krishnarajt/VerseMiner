import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # Options: "sqlite" or "postgres"

# PostgreSQL configuration (used if DB_TYPE=postgres)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "lyrics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# SQLite configuration (used if DB_TYPE=sqlite)
DB_ROOT_PATH = os.getenv("DB_ROOT_PATH", "db_data")
DB_PATH = os.getenv("DB_PATH", f"{DB_ROOT_PATH}/lyrics.db")

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Root path for music files
MUSIC_ROOT_PATH = os.getenv("MUSIC_ROOT_PATH", "/music")

# Whisper model configuration
WHISPER_MODEL = "large-v3"  # Most accurate model

# Supported audio formats
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".wma", ".aac"}
