# Polis

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-4.1.2-E25A1C?style=flat&logo=apachespark&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-3.2.2-017CEE?style=flat&logo=apacheairflow&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-1.11-FF694B?style=flat&logo=dbt&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5.3-FFF000?style=flat&logo=duckdb&logoColor=black)
![MongoDB](https://img.shields.io/badge/MongoDB-8.0-47A248?style=flat&logo=mongodb&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)

A data engineering pipeline and dashboard for the 2025 Philippine Midterm Elections. Built to make election data accessible and easy to understand for everyone.

<img width="1102" height="474" alt="image" src="https://github.com/user-attachments/assets/cb746a1b-51aa-4a47-bc12-90173060e590" />

---

## The idea

Election data in the Philippines is public but hard to work with. COMELEC releases results as raw files that require technical knowledge to explore. Polis takes that raw data, runs it through a full data engineering pipeline, and presents it as an interactive dashboard anyone can use.

This is not an authoritative report. The data has known gaps documented below.

---

## Dashboard

### Senate Results
<img width="1049" height="815" alt="image" src="https://github.com/user-attachments/assets/4ec559f5-be40-4671-abd7-9facd116caa0" />
<img width="1085" height="708" alt="image" src="https://github.com/user-attachments/assets/cb6dbf2a-0fba-4db6-bb58-cc8356a64438" />
<img width="1063" height="799" alt="image" src="https://github.com/user-attachments/assets/959135e3-bf7f-4991-a330-8144502bd61d" />

### Party List Results
<img width="1052" height="809" alt="image" src="https://github.com/user-attachments/assets/9229c75c-fa38-4bbe-a2cd-07fbea0bbfa4" />
<img width="1097" height="807" alt="image" src="https://github.com/user-attachments/assets/bf0e994d-dbc3-4dba-80dd-e7a43481cdf2" />
<img width="1052" height="809" alt="image" src="https://github.com/user-attachments/assets/5152d2f4-b1d4-4d96-b6d5-1719a2b7d0c5" />

### Regional Breakdown
<img width="1063" height="635" alt="image" src="https://github.com/user-attachments/assets/141e5608-0ad4-4e8d-a448-4dc056998d3b" />
<img width="1067" height="651" alt="image" src="https://github.com/user-attachments/assets/bcc5402a-d03d-4d19-8e90-621f6f052378" />
<img width="1047" height="820" alt="image" src="https://github.com/user-attachments/assets/589cdc44-440b-49aa-b5f0-b865698db455" />

Three pages:

- **Senate:** Final rankings for all 66 candidates, top 12 winners, vote totals by region
- **Party List:** All 156 parties ranked, seats awarded, qualified party highlights
- **Regional Breakdown:** Pick any candidate or party and see how they performed across all 17 regions

---

## Pipeline

```mermaid
flowchart LR
    A[COMELEC CSV Files] --> B[MongoDB\nRaw Landing Zone]
    B --> C[Apache Spark\nCleaning + Validation]
    C --> D[Parquet Files\nIntermediate Storage]
    D --> E[dbt + DuckDB\nStar Schema]
    E --> F[Streamlit\nDashboard]
    G[Apache Airflow] -.->|Orchestrates| C
```

---

## Architecture

```mermaid
flowchart TD
    subgraph Sources
        S1[senate25.csv\n92,822 rows]
        S2[partylist25.csv\n92,822 rows]
        S3[election_results_2025.csv\n20M rows]
    end

    subgraph Raw Landing
        M[(MongoDB\npolis database)]
        S1 --> M
        S2 --> M
        S3 --> M
    end

    subgraph Spark Jobs
        J1[clean_senate.py]
        J2[clean_partylist.py]
        J3[clean_results.py]
        M --> J1
        M --> J2
        M --> J3
    end

    subgraph Parquet
        P1[senate_25/]
        P2[partylist_25/]
        P3[election_results_2025/]
        J1 --> P1
        J2 --> P2
        J3 --> P3
    end

    subgraph DuckDB Star Schema
        F1[fact_ballots]
        F2[fact_votes]
        D1[dim_precinct]
        D2[dim_candidate]
        P1 --> F1
        P2 --> F1
        P3 --> F2
        P3 --> D1
        P3 --> D2
    end

    subgraph Dashboard
        ST[Streamlit App]
        F1 --> ST
        F2 --> ST
        D1 --> ST
        D2 --> ST
    end
```

---

## Star schema

```mermaid
erDiagram
    fact_votes {
        int precinct_id FK
        int candidate_id FK
        int votes
    }
    fact_ballots {
        int precinct_id FK
        int registered_voters
        int actual_voters
        int valid_ballot
        int over_votes
        int under_votes
        int obtained_votes
    }
    dim_precinct {
        int precinct_id PK
        int precinct_code
        text region
        text province
        text municipality
        text barangay
    }
    dim_candidate {
        int candidate_id PK
        text candidate_name
        text position
        text party
    }
    fact_votes }o--|| dim_precinct : "precinct_id"
    fact_votes }o--|| dim_candidate : "candidate_id"
    fact_ballots }o--|| dim_precinct : "precinct_id"
```

---

## Stack

| Layer | Tool |
|---|---|
| Ingestion | Python + PyMongo |
| Raw storage | MongoDB |
| Orchestration | Apache Airflow |
| Cleaning | Apache Spark (PySpark) |
| Intermediate storage | Parquet (uncompressed) |
| Warehouse | DuckDB + MotherDuck |
| Transformation | dbt |
| Dashboard | Streamlit |
| Notebooks | Marimo |

---

## Data sources

| File | Format | Rows | Use |
|---|---|---|---|
| senate25 | Wide CSV | 92,822 | Ballot integrity, vote totals |
| partylist25 | Wide CSV | 92,822 | Ballot integrity, vote totals |
| election_results_2025 | Long CSV | 20,138,577 | Geographic distribution |

---

## How to run

### View the dashboard

The live dashboard is hosted on Streamlit Community Cloud. No setup required.

To run it locally:

```bash
pip install -r requirements.txt
cp .env.example .env  # add your MOTHERDUCK_TOKEN
streamlit run streamlit/app.py
```

### Reproduce the full pipeline

Only needed if you want to re-run the pipeline from raw data.

**Prerequisites:** Docker Desktop (8GB RAM allocated), Python 3.11+

**1. Start the stack**
```bash
docker compose up -d
```

**2. Add raw data**

Place the three source CSV files in `datasets/`:
- `senate25-final_updated.csv`
- `partylist25-final_updated.csv`
- `philippines_2025_elections_2025_results.csv`

**3. Run the DAG**

Trigger the `polis_dag` at `http://localhost:8080`. Four steps run in sequence:

| Step | Task | Runtime |
|---|---|---|
| 1 | Ingest CSVs into MongoDB | ~5 min |
| 2 | Clean senate25 via Spark | ~10 min |
| 3 | Clean partylist25 via Spark | ~10 min |
| 4 | Clean election_results_2025 via Spark | ~23 min |

> Step 4 takes 23 minutes because the long-format file has 20M documents. Spark reads ~17M rows, runs three validation checks, deduplicates on `(PRECINCT_CODE, CANDIDATE_NAME)`, and writes uncompressed Parquet (ADR-008: Snappy is incompatible with ARM/aarch64). MongoDB is capped at 2GB to prevent OOM kills during the read phase.

**4. Build the warehouse**
```bash
dbt run --project-dir polis
dbt test --project-dir polis
```

**5. Run the dashboard**
```bash
streamlit run streamlit/app.py
```

---

## Known data gaps

**Vote totals:** The long-format file was scraped on 2025-08-21 before canvassing was complete. Totals in this file are lower than official COMELEC results. Senate and Party List pages use the wide-format files which reflect final certified results. Regional Breakdown uses the long-format file for geographic distribution only.

**Precinct coverage:** `dim_precinct` covers 77,615 of the 92,488 domestic precincts. The remaining 14,973 precincts exist in the wide-format files but have no rows in the long-format scrape. Documented in `docs/data-quality.md`.

**Scope:** Local government elections are excluded. Polis covers Senatorial and Party List races only.

**OAV and LAV:** Excluded from the Regional Breakdown map. Included in Senate and Party List totals.

---

## ADRs

Key decisions documented in `docs/ADR.md`:

- ADR-008: Parquet uncompressed (ARM/aarch64 Snappy incompatibility)
- ADR-009: DuckDB over PostgreSQL as analytical warehouse
- ADR-010: Two-fact-table star schema design
- ADR-011: Streamlit over SvelteKit + FastAPI

---

## Future scope

- Live choropleth map with Mapbox GL JS
- OAV and LAV inclusion in geographic breakdown
- Local government election results
- Cloud VM deployment for full pipeline re-runs
- `dim_precinct` rebuilt from wide-format files for complete precinct coverage
