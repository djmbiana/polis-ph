import glob
import os

import pandas as pd
import pytest

SPARK_OUTPUT = "/Users/derrick/Projects/polis-ph/spark/output"


def _parquet_files(subpath: str) -> list[str]:
    return glob.glob(os.path.join(SPARK_OUTPUT, subpath, "*.parquet"))


def _read_parquet(subpath: str, columns: list[str] | None = None) -> pd.DataFrame:
    files = _parquet_files(subpath)
    return pd.concat(
        [pd.read_parquet(f, columns=columns) for f in files],
        ignore_index=True,
    )


# ── directory / file existence ─────────────────────────────────────────────────

def test_senate_domestic_dir_exists():
    assert os.path.isdir(os.path.join(SPARK_OUTPUT, "senate_25", "domestic"))


def test_senate_domestic_has_parquet():
    assert len(_parquet_files("senate_25/domestic")) >= 1


def test_partylist_domestic_dir_exists():
    assert os.path.isdir(os.path.join(SPARK_OUTPUT, "partylist_25", "domestic"))


def test_partylist_domestic_has_parquet():
    assert len(_parquet_files("partylist_25/domestic")) >= 1


def test_results_dir_exists():
    assert os.path.isdir(os.path.join(SPARK_OUTPUT, "election_results_2025"))


def test_results_has_parquet():
    assert len(_parquet_files("election_results_2025")) >= 1


# ── row counts ─────────────────────────────────────────────────────────────────

def test_senate_domestic_row_count():
    df = _read_parquet("senate_25/domestic", columns=["REGION"])
    assert len(df) == 92_488


def test_results_row_count():
    df = _read_parquet("election_results_2025", columns=["VOTES"])
    assert len(df) == 17_152_915


# ── data quality ───────────────────────────────────────────────────────────────

def test_results_no_null_candidate_name():
    df = _read_parquet("election_results_2025", columns=["CANDIDATE_NAME"])
    assert df["CANDIDATE_NAME"].notna().all()


def test_results_no_negative_votes():
    df = _read_parquet("election_results_2025", columns=["VOTES"])
    assert (df["VOTES"] >= 0).all()
