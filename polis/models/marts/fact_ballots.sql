WITH senate AS (
  SELECT * FROM {{ ref('stg_senate_25') }}
),
precinct AS (
  SELECT * FROM {{ ref('dim_precinct') }}
)

SELECT p.PRECINCT_ID
       , senate.REGISTERED_VOTERS
       , senate.ACTUAL_VOTERS
       , senate.VALID_BALLOT
       , senate.OVER_VOTES
       , senate.UNDER_VOTES
       , senate.OBTAINED_VOTES
FROM senate
LEFT JOIN precinct p ON senate.MACHINE_ID = p.PRECINCT_CODE
