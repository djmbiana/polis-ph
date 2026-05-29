import os
from dotenv import load_dotenv
from pathlib import Path

# setting root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# loading the .env file
load_dotenv(REPO_ROOT / ".env")

# POSTGRES information
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
RAW_DATA_PATH = REPO_ROOT / os.getenv("RAW_DATA_PATH", "datasets")
DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
