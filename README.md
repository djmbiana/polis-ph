# polis-ph
An end-to-end data engineering pipeline for the 2025 Philippine midterm elections — Spark and dbt transforming precinct-level results into an interactive electoral story.

## Status
- Phase 1: Data Exploration  (DONE)
  - Explored wide-format datasets (senate25, partylist25); validated against COMELEC official records
  - The 3.1GB long-format file will be ingested in a later phase
- Phase 2: Pipeline Architecture & Batch Ingestion (DONE)
  - Raw CSVs → MongoDB (raw landing zone) → Spark (validation, cleaning, transformation) → Parquet
  - Airflow DAG orchestrates ingestion → senate cleaning → partylist cleaning
  - Docker stack: PostgreSQL, Spark, MongoDB, Airflow (scheduler, apiserver, triggerer, dag-processor)
- Phase 3: dbt + DuckDB Warehouse (in-progress)

## Architecture
RAW CSVs → MongoDB → Spark → Parquet → DuckDB → FastAPI → SvelteKit

Orchestrated by Apache Airflow (LocalExecutor).

## Data Sources
See `docs/data-source-inventory.md`

## Project Description
Polis is a live interactive map of the 2025 Philippine Midterm Election results. This election determines new Senators and Party List representatives within the House of Representatives.

The goal is to report and visualize vote counts per candidate and party list, and map which regions voted for them the most. Data is presented neutrally — this is not a political critique or agenda.

## Quickstart
```bash
cp .env.example .env
cp .env.docker.example .env.docker
docker compose up -d
docker exec polis-ph-airflow-scheduler-1 airflow dags reserialize
# Trigger polis_dag from Airflow UI at localhost:8080
```
