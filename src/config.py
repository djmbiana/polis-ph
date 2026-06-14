import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env", override=False)
except ImportError:
    pass

MONGO_URL = os.getenv("MONGO_URL", "")
RAW_DATA_PATH = REPO_ROOT / os.getenv("RAW_DATA_PATH", "datasets")
