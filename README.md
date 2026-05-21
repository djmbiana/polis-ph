# polis-ph
A end-to-end data engineering pipeline for the 2025 Philippine senate elections - Spark, and dbt transforming precinct-level results into an interactive electoral story.

## Status
Phase 1: Data Exploration (in progress)

## Data sources
See `docs/data-source-info.md`

## Project Description
Polis is an interactive map of the results of the 2025 Midterm Election. This election determines new Senators and Party Lists within the House of Representatives.
The intent behind this project is to report and map out the analytics of the vote count of each candidate and partylist and which region voted for them the most.
It is made to inform the general public on the results and is intended for public reference. The data is presented in a neutral manner, it is not a political critique or
pushing any personal agenda.
  
## Quickstart
```bash
cp .env.example .env
pip install -r requirements.txt
jupyter notebook notebooks/
```
