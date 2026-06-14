# Architecture Decision Log

This log records the architectural decisions made for this project.

---

## ADR-001: senate25 and partylist25 as primary EDA sources before touching the 3.1GB file
**Date:** 2026-05-19

### Context
I need to perform an EDA prior to feeding the larger data for processing to get a bigger picture on the type of data being contained.

### Decision
Start EDA with senate25 and partylist25 as these files are smaller, more manageable, and contain the same schema. The big file requires chunked loading and it is harder to explore interactively.

### Trade-offs
- **Good:** Smaller file size, less rows, data can be explored visually prior to further operations.
- **Bad:** LGU candidate data will not be available until the large file is processed.

---

## ADR-002: Wide-format files used for ballot integrity metrics; long-format file used for geographic coverage
**Date:** 2026-05-19

### Context
Different files serve different analytical purposes.

### Decision
senate25 and partylist25 contain overVotes, underVotes, and validVotes fields absent in the long-format file. This will be essential for ballot integrity analysis. The long-format file covers all positions including LGU candidates, and will serve as the primary source for the interactive map and regional breakdown.

### Trade-offs
- **Good:** Adds an analytical layer to the map of voters later on.
- **Bad:** Requires cross-validation between sources to ensure vote totals agree.

### Note
The long-format file is not loaded into the DAG as it runs for around 23 minutes on a local machine. It could be included later on during further improvement (ie: hosting on a cloud VM).

---

## ADR-003: PostgreSQL inside of Docker *(superseded by ADR-009)*
**Date:** 2026-05-19 · **Superseded:** 2026-06-14

### Context
The project requires a relational database to perform exploratory data analysis.

### Decision
Use PostgreSQL inside Docker for portability and to avoid dependency conflicts with other local projects. Mapped to port 5433 on the host to avoid conflicts with an existing Homebrew PostgreSQL instance running on 5432.

### Trade-offs
- **Good:** Portable, opens up the possibility to version control the database.
- **Bad:** Requires more setup.

### Supersession Note
PostgreSQL has been fully removed from the stack. DuckDB (ADR-009) handles all analytical queries. Airflow metadata was migrated from PostgreSQL to SQLite (`sqlite:////opt/airflow/airflow.db`). `sql/01_create_raw_schema.sql` and `sql/02_create_airflow_db.sql` have been deleted.

---

## ADR-004: Batch Processing instead of Streaming
**Date:** 2026-05-21

### Context
The project initially proposed streaming for data ingestion through Kafka. Upon further research, that would be overkill for the way election data is distributed nationwide.

### Considered
Considered streaming initially however upon reading Fundamentals of Data Engineering (CH.2), I learned that streaming should only be implemented if there is business value that can benefit from it. There is no such value provided in the election data.

### Trade-offs
- **Good:** Easier setup, fits the method in which election data is distributed in the Philippines (in batches every hour via precincts sharing their counts).
- **Bad:** Batch has higher latency compared to real-time data streaming as there is inherently always going to be a buffer state between each batch.

---

## ADR-005: Switched from Jupyter Notebook to Marimo
**Date:** 2026-05-25

### Context
A colleague suggested switching to Marimo due to its reactive nature fitting the dynamic nature of the exploration analysis.

### Considered
Sticking with Jupyter. Upon further research I found that I could greatly benefit from Marimo's reactivity. It is also easier to version control `.py` files as compared to Jupyter's `.ipynb` format.

### Trade-offs
- **Good:** Reactive cells, updates dependencies as changes are typed out.
- **Bad:** Marimo is a newer project and may not be compatible with some Python packages.

---

## ADR-006: MongoDB as the raw data landing zone
**Date:** 2026-05-25

### Context
MongoDB will be used as the landing zone for raw data due to the flexibility given by its schemaless architecture. Schema flexibility matters here because of the dataset's wide format with 66+ candidate columns. It would be easier to add more incoming data for future elections compared to strict relational schemas.

### Considered
Using a separate PostgreSQL schema known as "raw" and cleaning from there. MongoDB was chosen for its schemaless architecture, making changes in an environment that does not enforce strict schema rules easier before loading into the warehouse.

### Trade-offs
- **Good:** Schemaless architecture will allow data cleaning and manipulation to be faster and more flexible.
- **Bad:** Adds a pipeline failure point as a mapper is needed to convert MongoDB documents into a relational schema downstream.

---

## ADR-007: Airflow as the orchestration engine
**Date:** 2026-05-25

### Context
Polis requires an orchestration engine to ensure pipeline tasks run in the correct order with their dependencies satisfied. Without this, the pipeline risks running tasks on incomplete or missing data.

### Considered
- Dagster: rejected because it is data asset-centric rather than task-centric. Better suited for pipelines that treat data as products rather than sequential batch jobs.
- CRON jobs: rejected because they only schedule by time. They have no awareness of task dependencies or whether upstream steps completed successfully.
- No orchestration: rejected because without dependency management, tasks could run out of order or on stale data, leading to unpredictable pipeline failures.

### Trade-offs
- **Good:** Ensures all pipeline tasks run in the correct order with satisfied dependencies.
- **Bad:** Can add a failure point of misconfiguration. Airflow also adds infrastructure complexity as it requires its own database, scheduler, and API service.

---

## ADR-008: Parquet for intermediate data storage
**Date:** 2026-05-25

### Context
Apache Parquet will be used for intermediate data storage for the transformed data from MongoDB before being fed down the pipeline. Parquet also preserves schema between Spark and DuckDB which reduces complications of moving data down the pipeline.

### Considered
Keeping raw CSVs: rejected as CSVs take up more storage as they do not compress files into binary format.

### Note
Parquet compression is set to uncompressed (`spark.sql.parquet.compression.codec=none`). Snappy codec is incompatible with ARM/aarch64 (Apple Silicon), causing Spark jobs to fail during the write phase.

### Trade-offs
- **Good:** Columnar format enables fast queries, preserves schema and data types, natively supported by Spark and DuckDB.
- **Bad:** Not human-readable like CSV or JSON, updating individual records requires rewriting files, produces multiple part files instead of one.

---

## ADR-009: DuckDB instead of PostgreSQL
**Date:** 2026-06-03

### Context
DuckDB will be chosen instead of PostgreSQL due to Polis' OLAP focused workload. Its ability to run fast analytical queries and its native Parquet support simplifies the setup for the final dashboard. PostgreSQL has been fully removed from the stack. Airflow uses SQLite for its metadata database.

### Considered
PostgreSQL: rejected as Polis does not require transactional operations or concurrent writes to the database. It would also add additional infrastructural overhead as DuckDB does not require a server process.

### Trade-offs
- **Good:** Native Parquet support, fast analytical queries, no infrastructure needed.
- **Bad:** No built-in API, less mature ecosystem compared to PostgreSQL.

---

## ADR-010: Star Schema Design for Polis Analytical Warehouse
**Date:** 2026-06-11

### Context
Phase 3 required designing a star schema to serve two distinct analytical use cases: vote total analysis and geographic mapping. Three Parquet sources were available: senate25 (wide format, 92,822 rows), partylist25 (wide format, 92,822 rows), and election_results_2025 (long format, 17,152,915 rows). These sources have different grains and different levels of accuracy.

### Decision

**Two-fact-table design:** Two fact tables are used instead of one because the sources operate at different grains. `fact_ballots` is precinct-level and sourced from the wide-format files. `fact_votes` is candidate-precinct-level and sourced from the long-format file. Forcing both into a single fact table would require either duplicating ballot integrity metrics or losing candidate-level vote granularity.

**dim_precinct sourced from long-format file:** `dim_precinct` is built from `raw_election_results` because it is the only source that carries `PRECINCT_CODE` as a standalone column. The wide-format files use `MACHINE_ID` as the precinct identifier. The tradeoff is that `dim_precinct` only covers 77,615 precincts instead of the full 92,488 domestic precincts, leaving 14,973 rows in `fact_ballots` with a null `PRECINCT_ID`. This is documented in the data quality report.

**ELECTION_TYPE_DIM dropped:** An election type dimension was considered during schema design but rejected. The dataset only contains two position values (Senator and Party List). A dimension table for two static values adds unnecessary complexity. The `POSITION` column in `dim_candidate` serves this purpose.

**fact_ballots sources from senate25 only:** Both senate25 and partylist25 carry identical ballot integrity metrics per precinct. Unioning both would duplicate every precinct row. Senate25 is used as the sole source for `fact_ballots` since the values are the same across both files.

### Trade-offs
- **Good:** Clean separation of concerns between vote totals and ballot integrity, avoids grain conflicts.
- **Bad:** `fact_ballots` has 14,973 rows with null `PRECINCT_ID` due to partial long-format coverage.

---

## ADR-011: Streamlit as Presentation Layer
**Date:** 2026-06-13

### Context
The original Polis architecture specified SvelteKit + Mapbox GL JS + D3.js + Scrollama as the frontend, served by a FastAPI backend. Given OJT beginning next semester and the need to ship a complete portfolio piece, the frontend scope was reassessed.

### Decision
Replace SvelteKit + FastAPI with Streamlit connected to DuckDB via MotherDuck.

### Reasons
- Streamlit is Python-native, eliminating the context switch to JavaScript.
- DuckDB connects directly to Streamlit without an API layer.
- Streamlit Community Cloud provides a free public URL for portfolio visibility.
- The pipeline story remains intact: MongoDB > Spark > Parquet > DuckDB > dbt > Streamlit.
- A polished dashboard is more legible to hiring managers than an unfinished SvelteKit app.

### Trade-offs
- **Good:** Faster to ship, no frontend build tooling, free hosting.
- **Bad:** Mapbox GL JS choropleth map deferred to future scope, live scrollytelling narrative dropped in favour of a standard dashboard layout.

---

## ADR-012: MotherDuck for cloud DuckDB hosting
**Date:** 2026-06-14

### Context
Streamlit Community Cloud cannot access local DuckDB files. The initial approach of committing `polis.duckdb` to the repo was rejected when the materialized tables grew to 315MB, exceeding GitHub's 100MB file size limit.

### Decision
Use MotherDuck (DuckDB's managed cloud service) to host the `polis` database. The connection is handled via a token stored in Streamlit Community Cloud secrets and a local `.env` file.

### Reasons
- Free tier supports up to 10GB, sufficient for Polis.
- Native DuckDB connection string: `md:polis?motherduck_token=...`
- No changes required to the SQL layer. All dbt models and queries work unchanged.
- Keeps credentials out of the repo via environment variables.

### Trade-offs
- **Good:** Enables public deployment without committing large binary files to the repo.
- **Bad:** Adds an external dependency and requires a MotherDuck account to reproduce the full deployment.
