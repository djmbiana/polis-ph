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
| overVotes | Ballots where the voter selected more candidates than the allowed maximum (invalid). |
| underVotes | Ballots where the voter selected fewer candidates than the allowed maximum (still valid). |
| validVotes | The amount of votes which are valid |
| obtainedVotes | Total obtained votes per candidate |
  - The remaining columns are numeric and contain the total votes per candidate 
- Column names are camelCase, might be worth changing it to snake_case to fit python's style rules and to make it more readable

## Geographic Findings
- 20 unique regions (Expected 17, The 3 additional entries are OAV (Overseas Absentee Voting), LAV (Local Absentee Voting), and NIR (Negros Island Region) which are treated as region-level identifiers)
- 92 unique provinces (Expected 82, same reason as the regions)
- 25,592 unique barangays (Lower than the 42,011 national count due to COMELEC's clustered precinct system) 

## Candidate Findings
- Wide format: candidate votes stored as individual columns, one per candidate (66 total)
- Candidates tend to score higher vote shares in their home region (tested against Dela Rosa, Go, and Pangilinan)
- Top 12 winners align with COMELEC's official results (confirms dataset accuracy)

## Spark findings
- Total rows: 92,822 (domestic: 92,488, OAV: 234, LAV: 100)
- Validation checks passed: no negative values, no invalid turnout, all regions valid
- Parquet output written to spark/output/senate_25/ and spark/output/partylist_25/

## Election_Results_2025 Findings
- String data types act as metadata to inform on details regarding the election such as names, geographic location, data sources.

| Column | What it means |
|---|---|
| Election_Type | Pertains to the election type in which the vote is being counted for ('Senatorial', 'Partylist', etc.) |
| Region | Pertains to the region in the phillippines in where the voting took place |
| Province | Pertains to which province in the Philippines |
| Municipality | Pertains to which municipality within the Philippines |
| Barangay | Pertains to which Barangay within the Phillippines |
| Candidate_Name | The name of the candidate  |
| Position | The position the candidate is running for |
| Party | The political party that the candidate is part of |
| Scraped_At | The date in which the data was scraped |
| Source | Where the data was scraped (in this case, COMELEC) |

- Numeric data types take the form of Integers. They account for votes, voters, precinct code.

| Column | What it means |
|---|---|
| Year | Year in which the vote was castedf |
| Precinct_Code | The code of the specific precinct used for voting |
| Votes | The votes given to a specific candidate |
| Total_Voters | The number of voters who voted within the precinct |
| Total_Votes | The total number of votes made in the precinct |
| Percentage | Only float. This is the percentage of vote share per precinct |
| Contest_ID | Represents the ID of the given contest. It was set to 0 for all rows. |
| Candidate_ID | Represents the ID of the given candidate. It was set to 0 for all rows.|

- Because of contest_id and candidate_id being set to 0, we will filter it out later on for geographic analysis.
- The vote counts of this are less accurate than senate_25 and candidate_25, so this dataset will be used for geographic analysis instead.
