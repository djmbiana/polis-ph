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
The project initally proposed streaming to the interactive site through Kafka.
Upon further research, that would be overkill for the way election data is distributed across the news.

### Considered
Considered using Kafka to slowly feed the datasets through Kafka. Rejected as that would make little to no measurable impact on the way
data is fed to the live dashboard

### Trade-offs
- **Good:** Easier setup, Fits the method in which election data is distributed in the Philippines (in batches every hour via precinct's sharing their counts)
- **Bad:** We lose speed (batch has more volume however it loses the speed given by data streaming)
