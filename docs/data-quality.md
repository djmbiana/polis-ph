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
