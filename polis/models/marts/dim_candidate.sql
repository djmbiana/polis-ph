WITH source AS (
  SELECT DISTINCT
    CANDIDATE_NAME
    , POSITION
    , PARTY
  FROM {{ ref('stg_results') }}
)
SELECT row_number() OVER() AS CANDIDATE_ID
       , CANDIDATE_NAME
       , POSITION
       , PARTY
FROM source
