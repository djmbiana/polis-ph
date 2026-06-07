import os
from pathlib import Path

from dotenv import load_dotenv

# setting root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# loading the .env file
load_dotenv(REPO_ROOT / ".env")

# POSTGRES information
DB_HOST = os.getenv("HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

RAW_DATA_PATH = REPO_ROOT / os.getenv("RAW_DATA_PATH", "datasets")
DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{DB_HOST}:27017"
