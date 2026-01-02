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
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemma-3-27b-it")


# Root path for music files
MUSIC_ROOT_PATH = os.getenv("MUSIC_ROOT_PATH", "/music")

# Whisper model configuration
WHISPER_ENGINE = os.getenv("WHISPER_ENGINE", "faster")  # Options: "openai" or "faster"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")  # For openai-whisper
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")  # Options: "cuda" or "cpu"

# Faster-whisper specific settings (used if WHISPER_ENGINE=faster)
FASTER_WHISPER_MODEL = os.getenv(
    "FASTER_WHISPER_MODEL", "medium"
)  # small, medium, large-v2, large-v3
FASTER_WHISPER_COMPUTE_TYPE = os.getenv(
    "FASTER_WHISPER_COMPUTE_TYPE", "int8"
)  # int8, float16, float32

# Supported audio formats
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".wma", ".aac"}
