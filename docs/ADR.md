# Architecture Decision Log

This log records the architectural decisions made for this project.

---

## ADR-001: `senate25` and `partylist25` as primary EDA sources before touching the 3.1GB file
**Date:** 2026-05-19

### Context
I need to perform an EDA prior to feeding the larger data for processing to get a bigger picture on the type of data being contained.

### Decision
Start EDA with `senate25` and partylist25` as these files are smaller, more manageable, and contain the same schema. The big file
requires chunked loading and it's harder to explore interactively. 

### Trade-offs
- **Good:** Smaller file size, Less rows, Data can be explored visually prior to further operations.
- **Bad:** LGU candidate data will not be available until the large file is processed.

---

## ADR-002: Wide-format files (senate25, partylist25) used for ballot integrity metrics; long-format file used for LGU coverage
**Date:** 2026-05-19

### Context
Different files serve different analytical purposes.

### Decision
senate25 and partylist25 contain overVotes, underVotes, validVotes fields absent in the big file. This will be essential for ballot integrity analysis.
The long-format file covers all positions including LGU candidates, and will serve as the primary source for the interactive map and scrollytelling layer.

### Trade-offs
- **Good:** Adds an analytical layer to the map of voters later on.
- **Bad:** Requires cross-validation between sources to ensure vote totals agree.

### NOTE:
- The long-format file will not loaded into the DAG as it runs for around 23 minutes on my local machine. It could be included later on during further improvement (ie: hosting on a cloud vm)

---

## ADR-003: PostgreSQL inside of Docker
**Date:** 2026-05-19

### Context
The project requires a relational database to perform exploratory data analysis.

### Considered
Considered using a local PostgreSQL install via Homebrew. Rejected in favour of Docker for easier portability
and to avoid dependency conflicts with other local projects. PostgreSQL inside Docker is mapped to port 5433 on
the host to avoid conflicts with the existing Homebrew PostgreSQL instance running on 5432.


### Trade-offs
- **Good:** Portable, Opens up the possibility to version control the database.
- **Bad:** Requires more set up.

---
## ADR-004: Opted to implement Batch Processing instead of Streaming
**Date:** 2026-05-21

### Context
The project initially proposed streaming for data ingestion through Kafka.
Upon further research, that would be overkill for the way election data is distributed nationwide.

## Considered
Considered streaming initally however upon reading Fundamentals of Data Engineering (CH.2), I learned that streaming should only
be implemented if there is business value that can benefit from it. There is no such value provided in the election data.

### Trade-offs
- **Good:** Easier setup, Fits the method in which election data is distributed in the Philippines (in batches every hour via precinct's sharing their counts)
- **Bad:** Batch has higher latency compared to real-time data streaming as there is inhernetly always going to be a buffer state between each batch.

---
## ADR-005: Switched from Jupyter Notebook to Marimo
**Date:** 2026-05-25

### Context
A colleague suggested that I switch to Marimo due to its reactive nature fitting the dynamic nature of my exploration analysis.

## Considered
Sticking with Jupyter, upon further research and reading I found that I could greatly benefit from Marimo's reactivity. It is also harder to
version control `.ipynb` files as compared to Marimo keeping everything in `.py` (raw python).

## Trade-offs
- **Good:** Reactive cells, updates dependencies as changes are typed out.
- **Bad:** Marimo is a new project, it might not be compatible with some python packages

---
## ADR-006: MongoDB will be the raw data landing zone

### Context
MongoDB will be used as the landing zone for raw data due to the flexibility given by no predefined schema.
Schema flexibility matters here because of the dataset's wide format with 66+ candidate columns. It would be easier to add more
incoming data for future elections compared to strict relational schemas.

## Considered
Using a separate postgres schema known as "raw" and cleaning from there.  MongoDB was chosen for its schemaless architecture
making changes in an environment that doesnt enforce strict schema rules will allow data cleaning, updating, or inserting easier
before even loading it into the warehouse.

## Trade-offs
- **Good:** Schemaless architecture will allow data cleaning and manipulation to be faster and flexible as they do not have the same rules as a strict SQL schema.
- **Bad:** Adds pipeline failure point as we will have to add a mapper that converts MongoDB documents into PostgreSQL's relational schema

---
## ADR-007: Airflow as the orchestration engine

## Context
Polis requires an orchestration engine to ensure pipeline tasks run in the correct order with their
dependencies satisfied. Without this, the pipeline risks running tasks on incomplete or missing data,
which would corrupt the interactive map.

## Considered
- Dagster: rejected because it is data asset-centric rather than task-centric. Better suited for pipelines that treat data as products rather than sequential batch jobs.
- CRON jobs: rejected because they only schedule by time. They have no awareness of task dependencies or whether upstream steps completed successfully.
- No orchestration at all: rejected because without dependency management, tasks could run out of order or on stale data, leading to unpredictable pipeline failures.


## Trade-offs
- **Good:** Airflow will ensure that all pipeline tasks run in correct order with satisfied dependencies
- **Bad:** Can add a failure point of misconfiguration. If Airflow is not configured properly it may cause no data to be pushed at all, breaking the whole pipeline; it also adds infrastructure complexity as Airflow requires its own database, scheduler, and API service.

---
## ADR-008: Parquet for intermediate data storage

## Context
Apache Parquet will be used for intermediate data storage for the transformed data from mongodb before being fed down the pipeline.
This will be used to minimize the storage space due to parquet compressing and managing the data into directories. Parquet also preserves schema between Spark and DuckDB which will reduce the complications of moving data down the pipeline.

## Considered
Keeping it as raw CSV's: rejected as csv's will take up more storage as it does not compress files into binary format (as compared to parquet)

## Trade-offs
- **Good:** Columnar Data (makes it easier to transport down the pipeline.), Columnar format enables fast queries, Preserves schema and data types, Natively supported by Spark, DuckDB, and many analytical tools.
- **Bad:** Not human-readable like CSV or JSON, Updating individual records is difficult (files are typically re-written), produces multiple files instead of 1 file.

---
## ADR-009: DuckDB instead of PostgreSQL 

## Context
DuckDB will be chosen instead of PostgreSQL due to polis' OLAP focused workload. It's ability to have fast analytical queries and native parquet support will simplify a lot of the set up for the final dashboard site.

PostgreSQL remains in the stack exclusively for Airflow metadata storage as per ADR-003.

## Considered
- PostgreSQL: rejected as polis does not require transactional operations or concurrent writes to the database. And because it would add additional infrastructural overhead (duckdb does not require a server file).

## Trade-offs
- **Good:** Native parquet support, fast analytical queries, no infrastructure needed
- **Bad:** No built in API, Web doesn't have native duckdb support (it has to talk to fastapi first), Less mature ecosystem as compared to postgres

---
## ADR-010: Star Schema Design for Polis Analytical Warehouse

## Context
Phase 3 required designing a star schema to serve two distinct analytical use cases: 
vote total analysis and geographic mapping. Three Parquet sources were available:
senate25 (wide format, 92,822 rows), partylist25 (wide format, 92,822 rows), and
election_results_2025 (long format, 17,152,915 rows). These sources have different
grains and different levels of accuracy.

## Decisions

### Two-Fact-Table Design
We use two fact tables instead of one because the sources operate at different grains.
`fact_ballots` is precinct-level and sourced from the wide-format files. `fact_votes`
is candidate-precinct-level and sourced from the long-format file. Forcing both into
a single fact table would require either duplicating ballot integrity metrics or losing
candidate-level vote granularity.

### dim_precinct Sourced from Long-Format File
`dim_precinct` is built from `raw_election_results` because it is the only source that
carries `PRECINCT_CODE` as a standalone column. The wide-format files use `MACHINE_ID`
as the precinct identifier. The tradeoff is that `dim_precinct` only covers 77,615
precincts instead of the full 92,488 domestic precincts, leaving 14,973 rows in
`fact_ballots` with a null `PRECINCT_ID`. This is documented in the data quality report.

### ELECTION_TYPE_DIM Dropped
An election type dimension was considered during schema design but rejected. The dataset
only contains two position values ("Senator" and "Party List"). A dimension table for
two static values adds unnecessary complexity. The `POSITION` column in `dim_candidate`
serves this purpose.

### fact_ballots Sources from Senate25 Only
Both senate25 and partylist25 carry identical ballot integrity metrics per precinct
(registered voters, actual voters, valid ballots, over/under votes). Unioning both
would duplicate every precinct row. Senate25 is used as the sole source for
`fact_ballots` since the values are the same across both files.

## Consequences
- `fact_ballots` has 14,973 rows with null `PRECINCT_ID` due to partial long-format coverage
- Vote total analysis must use `fact_votes` aggregated from the long-format file, with
  the caveat that totals are lower than official COMELEC results (mid-canvassing scrape)
- For authoritative vote totals, the wide-format staging models should be queried directly

---
## ADR-011: Streamlit as Presentation Layer

## Context
The original Polis architecture specified SvelteKit + Mapbox GL JS + D3.js + Scrollama
as the frontend, served by a FastAPI backend. This was scoped for a live interactive
site. Given OJT beginning next semester and the need to ship a complete portfolio piece,
the frontend scope was reassessed.

## Decision
Replace SvelteKit + FastAPI with Streamlit connected directly to DuckDB.

## Reasons
- Streamlit is Python-native, eliminating the context switch to JavaScript
- DuckDB connects directly to Streamlit without an API layer
- Streamlit Community Cloud provides a free public URL for portfolio visibility
- The pipeline story remains intact: MongoDB -> Spark -> Parquet -> DuckDB -> dbt -> Streamlit
- A polished dashboard is more legible to hiring managers than an unfinished SvelteKit app

## Consequences
- Mapbox GL JS choropleth map is deferred to a future scope when the project is hosted
  on a cloud VM with sufficient resources
- The live scrollytelling narrative is dropped in favor of a standard dashboard layout
- Streamlit Community Cloud requires the DuckDB file to be bundled with the app or
  hosted on accessible storage
