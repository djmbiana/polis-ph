# polis-ph
An end-to-end data engineering pipeline for the 2025 Philippine midterm elections — Spark and dbt transforming precinct-level results into an interactive electoral story.

## Status
Phase 1: Data Exploration (in progress)

## Data Sources
See `docs/data-source-inventory.md`

## Project Description
Polis is a live interactive map of the 2025 Philippine Midterm Election results. This election determines new Senators and Party List representatives within the House of Representatives.

The goal is to report and visualize vote counts per candidate and party list, and map which regions voted for them the most. Data is presented neutrally (this is not a political critique or agenda.)

## Quickstart
\`\`\`bash
cp .env.example .env
pip install -r requirements.txt
docker compose up -d
python src/ingestion.py
\`\`\`
