WITH votes AS (
  SELECT * FROM {{ ref('stg_results') }}
),
precinct AS (
  SELECT * FROM {{ ref('dim_precinct') }}
),
candidate AS (
  SELECT * FROM {{ ref('dim_candidate') }}
)

SELECT p.PRECINCT_ID
       , c.CANDIDATE_ID
       , v.VOTES
FROM votes v
LEFT JOIN precinct p ON v.PRECINCT_CODE = p.PRECINCT_CODE
LEFT JOIN candidate c ON v.CANDIDATE_NAME = c.CANDIDATE_NAME
