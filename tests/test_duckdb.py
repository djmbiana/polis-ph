TABLES = [
    "dim_precinct",
    "dim_candidate",
    "fact_votes",
    "fact_ballots",
    "mart_senate_rankings",
    "mart_partylist_rankings",
]


def test_all_tables_exist(duckdb_con):
    existing = {row[0] for row in duckdb_con.execute("SHOW TABLES").fetchall()}
    for table in TABLES:
        assert table in existing, f"Table {table!r} not found in DuckDB"


def test_dim_precinct_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM dim_precinct").fetchone()[0]
    assert count == 77_615


def test_dim_candidate_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM dim_candidate").fetchone()[0]
    assert count == 221


def test_fact_votes_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM fact_votes").fetchone()[0]
    assert count == 17_152_915


def test_fact_ballots_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM fact_ballots").fetchone()[0]
    assert count == 92_488


def test_mart_senate_rankings_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM mart_senate_rankings").fetchone()[0]
    assert count == 66


def test_mart_partylist_rankings_row_count(duckdb_con):
    count = duckdb_con.execute("SELECT COUNT(*) FROM mart_partylist_rankings").fetchone()[0]
    assert count == 155


def test_exactly_12_senate_winners(duckdb_con):
    count = duckdb_con.execute(
        "SELECT COUNT(*) FROM mart_senate_rankings WHERE WINNER = true"
    ).fetchone()[0]
    assert count == 12


def test_partylist_total_seats_at_most_63(duckdb_con):
    total = duckdb_con.execute(
        "SELECT SUM(SEATS) FROM mart_partylist_rankings"
    ).fetchone()[0]
    assert total <= 63


def test_no_negative_fact_votes(duckdb_con):
    count = duckdb_con.execute(
        "SELECT COUNT(*) FROM fact_votes WHERE VOTES < 0"
    ).fetchone()[0]
    assert count == 0


def test_no_negative_ballot_values(duckdb_con):
    count = duckdb_con.execute(
        "SELECT COUNT(*) FROM fact_ballots "
        "WHERE REGISTERED_VOTERS < 0 OR ACTUAL_VOTERS < 0 OR VALID_BALLOT < 0"
    ).fetchone()[0]
    assert count == 0


def test_senate_rank1_is_go_bong_go(duckdb_con):
    name = duckdb_con.execute(
        "SELECT CANDIDATE_NAME FROM mart_senate_rankings WHERE RANK = 1"
    ).fetchone()[0]
    assert "GO, BONG GO" in name


def test_senate_vote_percentage_sums_to_100(duckdb_con):
    total = duckdb_con.execute(
        "SELECT SUM(VOTE_PERCENTAGE) FROM mart_senate_rankings"
    ).fetchone()[0]
    assert abs(total - 100.0) < 0.1
