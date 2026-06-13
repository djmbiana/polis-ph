with source AS(
  SELECT DISTINCT
    PRECINCT_CODE
    , REGION
    , PROVINCE 
    , MUNICIPALITY
    , BARANGAY
  FROM {{ ref('stg_results') }}
)

SELECT row_number() OVER() AS PRECINCT_ID
       , PRECINCT_CODE
       , REGION
       , PROVINCE
       , MUNICIPALITY
       , BARANGAY
FROM source
