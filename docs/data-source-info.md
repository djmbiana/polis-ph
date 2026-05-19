# Information on Data Sources

## Data Sources & Metadata

| Name | Source | No. of Records | Size | Dataset Type |
|---|---|---|---|---|
| philippines_2025_elections_2025_results | Google drive (Scraped by my collegue) | 20,138,578 | 3.8GB | Long |
| partylist25-final_updated | https://figshare.com/articles/dataset/29086472 | 92,823 | 37.3MB | Wide |
| senate25-final_updated | https://figshare.com/articles/dataset/29086472 | 92,823 | 26.9MB | Wide |

## Findings
- `partylist-25` and `senate-25` have a wide dataset type and they contain more information regarding votes (including valid ballots, over votes, under votes, and valid votes).
  As compared to `philippines_2025_elections` which has it confined to one row. 
- `partylist25` and `senate25` have significantly fewer records than `philippines_2025_elections` because they represent precinct-level summaries, not individual candidate rows. They should not be treated as a subset of the full dataset,
  they are the same underlying data in a different shape, with the full file additionally covering LGU candidates.
