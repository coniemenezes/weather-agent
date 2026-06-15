import os

from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv(
    "SUPABASE_DB_URI"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

GEMINI_TEMPERATURE = float(
    os.getenv(
        "GEMINI_TEMPERATURE",
        "0"
    )
)

THREAD_ID = os.getenv(
    "THREAD_ID",
    "weather-session"
)

CHECKPOINTER_BACKEND = os.getenv(
    "CHECKPOINTER_BACKEND",
    "sqlite"
)

SQLITE_DB_PATH = os.getenv(
    "SQLITE_DB_PATH",
    "checkpoints.db"
)

SUPABASE_DB_URI = os.getenv(
    "SUPABASE_DB_URI"
)

API_WEATHER = os.getenv(
    "API_WEATHER"
)