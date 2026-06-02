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
