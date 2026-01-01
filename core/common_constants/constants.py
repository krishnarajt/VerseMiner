import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "lyrics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Root path for music files
MUSIC_ROOT_PATH = os.getenv("MUSIC_ROOT_PATH", "/music")

# Whisper model configuration
WHISPER_MODEL = "large-v3"  # Most accurate model

# Supported audio formats
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".opus", ".wma", ".aac"}
