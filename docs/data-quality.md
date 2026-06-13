# Data Quality Report

## Senate_25 Schema Findings
- Object data types take the form of strings and they describe where the voting takes place

| Column | What it means |
|---|---|
| Region | Pertains to the region in the Philippines |
| Province | Pertains to which province in the Philippines |
| Municipality | Pertains to the municipality of each province |
| Barangay | Pertains to which barangay in each municipality |

- Numeric data types (int64) inform us about the details within each precinct

| Column | What it means |
|---|---|
| machineId | The id of the Vote Counting Machine which processed the votes |
| registeredVoters | The amount of voters who are registered per precinct |
| actualVoters | The amount of voters who actually voted |
| validBallot | The amount of ballots that are valid within each precinct |
| overVotes | Ballots where the voter selected more candidates than the allowed maximum (invalid) |
| underVotes | Ballots where the voter selected fewer candidates than the allowed maximum (still valid) |
| validVotes | The amount of votes which are valid |
| obtainedVotes | Total obtained votes per candidate |

- The remaining columns are numeric and contain the total votes per candidate
- Column names are camelCase, changed to SCREAMING_SNAKE_CASE in the Spark cleaning job to follow Python conventions and improve readability

## Geographic Findings
- 20 unique regions (Expected 17. The 3 additional entries are OAV (Overseas Absentee Voting), LAV (Local Absentee Voting), and NIR (Negros Island Region) which are treated as region-level identifiers)
- 92 unique provinces (Expected 82, same reason as the regions)
- 25,592 unique barangays (Lower than the 42,011 national count due to COMELEC's clustered precinct system)

## Candidate Findings
- Wide format: candidate votes stored as individual columns, one per candidate (66 total)
- Candidates tend to score higher vote shares in their home region (tested against Dela Rosa, Go, and Pangilinan)
- Top 12 winners align with COMELEC's official results (confirms dataset accuracy)

## Spark Findings
- Total rows: 92,822 (domestic: 92,488, OAV: 234, LAV: 100)
- Validation checks passed: no negative values, no invalid turnout, all regions valid
- Parquet output written to spark/output/senate_25/ and spark/output/partylist_25/

## Election_Results_2025 Findings
- String data types act as metadata to inform on details regarding the election such as names, geographic location, and data sources

| Column | What it means |
|---|---|
| Election_Type | Pertains to the election type in which the vote is being counted for ('Senatorial', 'Partylist', etc.) |
| Region | Pertains to the region in the Philippines in where the voting took place |
| Province | Pertains to which province in the Philippines |
| Municipality | Pertains to which municipality within the Philippines |
| Barangay | Pertains to which Barangay within the Philippines |
| Candidate_Name | The name of the candidate |
| Position | The position the candidate is running for |
| Party | The political party that the candidate is part of |
| Scraped_At | The date in which the data was scraped |
| Source | Where the data was scraped (in this case, COMELEC) |

- Numeric data types take the form of integers. They account for votes, voters, and precinct code

| Column | What it means |
|---|---|
| Year | Year in which the vote was casted |
| Precinct_Code | The code of the specific precinct used for voting |
| Votes | The votes given to a specific candidate |
| Total_Voters | The number of voters who voted within the precinct |
| Total_Votes | The total number of votes made in the precinct |
| Percentage | Only float. This is the percentage of vote share per precinct |
| Contest_ID | Represents the ID of the given contest. Set to 0 for all rows |
| Candidate_ID | Represents the ID of the given candidate. Set to 0 for all rows |

- Contest_ID and Candidate_ID were dropped in the Spark cleaning job as they carry no analytical value
- Vote counts in this dataset are lower than senate_25 and partylist_25 because it was scraped mid-canvassing on 2025-08-21. This dataset is used for geographic analysis only

## Known Data Gaps

### fact_ballots -- Null PRECINCT_ID (14,973 rows)

**Discovered:** Phase 3 dbt test run
**Severity:** Low

**Description:**
14,973 precincts in the senate25 wide-format file have no corresponding rows in raw_election_results. This causes fact_ballots.PRECINCT_ID to be null for these rows after the join to dim_precinct.

**Root Cause:**
dim_precinct is built from raw_election_results (long format), which was scraped on 2025-08-21 before canvassing was complete. The wide-format files were validated against final COMELEC official results and are the authoritative source for vote totals.

**Impact:**
- fact_ballots ballot integrity metrics are still accurate for all 92,488 precincts
- Geographic drill-down via dim_precinct is unavailable for the 14,973 affected precincts
- fact_votes and dim_precinct are unaffected

**Resolution:**
Accepted as a known limitation. A future improvement would be to build dim_precinct from the wide-format files to achieve full precinct coverage.

## Cross-Validation Findings

### senate25 vs raw_election_results vote totals

**Discovery:** Phase 3 - 04_cross_validation.py

**Finding:**
Wide-format senate25 totals are consistently higher than long-format totals across all candidates. Differences range from thousands to around 100k votes per candidate.

**Root Cause:**
raw_election_results was scraped on 2025-08-21 before canvassing was complete. The wide-format files reflect final COMELEC certified results.

**Decision:**
- Wide-format files (senate25, partylist25) are the authoritative source for vote total analysis
- raw_election_results is used exclusively for geographic distribution and precinct-level mapping
