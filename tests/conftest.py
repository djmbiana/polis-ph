import pytest
import duckdb

DB_PATH = "/Users/derrick/Projects/polis-ph/polis.duckdb"


@pytest.fixture
def duckdb_con():
    con = duckdb.connect(DB_PATH, read_only=True)
    yield con
    con.close()
