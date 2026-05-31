-- Exploration Queries

-- =============================================
-- SENATE_25 EXPLORATION QUERIES
-- =============================================

-- Verifying row count (expected: 92,822) 
SELECT COUNT(*) AS total_votes
FROM raw.senate_25;

-- Unique  counts per geographic data
SELECT
    COUNT(DISTINCT region) AS regions
    , COUNT(DISTINCT province) AS provinces
    , COUNT(DISTINCT municipality) AS municipalities
    , COUNT(DISTINCT barangay) AS barangays
FROM raw.senate_25;

-- Number of precincts per region 
SELECT region
	   , COUNT(*) AS precinct_count
FROM raw.senate_25
GROUP BY region
ORDER BY precinct_count DESC;

-- Top senators by vote
SELECT candidate, total_votes
FROM (
    SELECT '1. ABALOS, BENHUR (PFP)' AS candidate, SUM("1. ABALOS, BENHUR (PFP)") AS total_votes FROM raw.senate_25
    UNION ALL
    SELECT '2. ADONIS, JEROME (MKBYN)', SUM("2. ADONIS, JEROME (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '3. AMAD, WILSON (IND)', SUM("3. AMAD, WILSON (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '4. ANDAMO, NARS ALYN (MKBYN)', SUM("4. ANDAMO, NARS ALYN (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '5. AQUINO, BAM (KNP)', SUM("5. AQUINO, BAM (KNP)") FROM raw.senate_25
    UNION ALL
    SELECT '6. ARAMBULO, RONNEL (MKBYN)', SUM("6. ARAMBULO, RONNEL (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '7. ARELLANO, ERNESTO (KTPNAN)', SUM("7. ARELLANO, ERNESTO (KTPNAN)") FROM raw.senate_25
    UNION ALL
    SELECT '8. BALLON, ROBERTO (IND)', SUM("8. BALLON, ROBERTO (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '9. BINAY, ABBY (NPC)', SUM("9. BINAY, ABBY (NPC)") FROM raw.senate_25
    UNION ALL
    SELECT '10. BONDOC, JIMMY (PDPLBN)', SUM("10. BONDOC, JIMMY (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '11. BONG REVILLA,RAMON, JR.(LAKAS)', SUM("11. BONG REVILLA,RAMON, JR.(LAKAS)") FROM raw.senate_25
    UNION ALL
    SELECT '12. BOSITA, COLONEL (IND)', SUM("12. BOSITA, COLONEL (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '13. BROSAS, ARLENE (MKBYN)', SUM("13. BROSAS, ARLENE (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '14. CABONEGRO, ROY (DPP)', SUM("14. CABONEGRO, ROY (DPP)") FROM raw.senate_25
    UNION ALL
    SELECT '15. CAPUYAN, ALLEN (PPP)', SUM("15. CAPUYAN, ALLEN (PPP)") FROM raw.senate_25
    UNION ALL
    SELECT '16. CASIÑO, TEDDY (MKBYN)', SUM("16. CASIÑO, TEDDY (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '17. CASTRO, TEACHER FRANCE (MKBYN)', SUM("17. CASTRO, TEACHER FRANCE (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '18. CAYETANO, PIA (NP)', SUM("18. CAYETANO, PIA (NP)") FROM raw.senate_25
    UNION ALL
    SELECT '19. D''ANGELO, DAVID (BUNYOG)', SUM("19. D'ANGELO, DAVID (BUNYOG)") FROM raw.senate_25
    UNION ALL
    SELECT '20. DE ALBAN,ATTORNEY ANGELO (IND)', SUM("20. DE ALBAN,ATTORNEY ANGELO (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '21. DE GUZMAN, KA LEODY (PLM)', SUM("21. DE GUZMAN, KA LEODY (PLM)") FROM raw.senate_25
    UNION ALL
    SELECT '22. DELA ROSA, BATO (PDPLBN)', SUM("22. DELA ROSA, BATO (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '23. DORINGO, NANAY MIMI (MKBYN)', SUM("23. DORINGO, NANAY MIMI (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '24. ESCOBAL, ARNEL (PM)', SUM("24. ESCOBAL, ARNEL (PM)") FROM raw.senate_25
    UNION ALL
    SELECT '25. ESPIRITU, LUKE (PLM)', SUM("25. ESPIRITU, LUKE (PLM)") FROM raw.senate_25
    UNION ALL
    SELECT '26. FLORANDA, MODY PISTON (MKBYN)', SUM("26. FLORANDA, MODY PISTON (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '27. GAMBOA, MARC LOUIE (IND)', SUM("27. GAMBOA, MARC LOUIE (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '28. GO, BONG GO    (PDPLBN)', SUM("28. GO, BONG GO    (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '29. GONZALES, NORBERTO (PDSP)', SUM("29. GONZALES, NORBERTO (PDSP)") FROM raw.senate_25
    UNION ALL
    SELECT '30. HINLO, JAYVEE (PDPLBN)', SUM("30. HINLO, JAYVEE (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '31. HONASAN, GRINGO (RP)', SUM("31. HONASAN, GRINGO (RP)") FROM raw.senate_25
    UNION ALL
    SELECT '32. JOSE, RELLY JR. (KBL)', SUM("32. JOSE, RELLY JR. (KBL)") FROM raw.senate_25
    UNION ALL
    SELECT '33. LACSON, PING (IND)', SUM("33. LACSON, PING (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '34. LAMBINO,  RAUL  (PDPLBN)', SUM("34. LAMBINO,  RAUL  (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '35. LAPID, LITO (NPC)', SUM("35. LAPID, LITO (NPC)") FROM raw.senate_25
    UNION ALL
    SELECT '36. LEE, MANOY WILBERT (AKSYON)', SUM("36. LEE, MANOY WILBERT (AKSYON)") FROM raw.senate_25
    UNION ALL
    SELECT '37. LIDASAN, AMIRAH (MKBYN)', SUM("37. LIDASAN, AMIRAH (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '38. MARCOLETA, RODANTE (IND)', SUM("38. MARCOLETA, RODANTE (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '39. MARCOS, IMEE R. (NP)', SUM("39. MARCOS, IMEE R. (NP)") FROM raw.senate_25
    UNION ALL
    SELECT '40. MARQUEZ, NORMAN (IND)', SUM("40. MARQUEZ, NORMAN (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '41. MARTINEZ, ERIC (IND)', SUM("41. MARTINEZ, ERIC (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '42. MATA, DOC MARITES (IND)', SUM("42. MATA, DOC MARITES (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '43. MATULA,  ATTY.  SONNY (WPP)', SUM("43. MATULA,  ATTY.  SONNY (WPP)") FROM raw.senate_25
    UNION ALL
    SELECT '44. MAZA, LIZA (MKBYN)', SUM("44. MAZA, LIZA (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '45. MENDOZA, HEIDI (IND)', SUM("45. MENDOZA, HEIDI (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '46. MONTEMAYOR,  JOEY  (IND)', SUM("46. MONTEMAYOR,  JOEY  (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '47. MUSTAPHA, SUBAIR (WPP)', SUM("47. MUSTAPHA, SUBAIR (WPP)") FROM raw.senate_25
    UNION ALL
    SELECT '48. OLIVAR, JOSE JESSIE (IND)', SUM("48. OLIVAR, JOSE JESSIE (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '49. ONG, DOC WILLIE (AKSYON)', SUM("49. ONG, DOC WILLIE (AKSYON)") FROM raw.senate_25
    UNION ALL
    SELECT '50. PACQUIAO, MANNY PACMAN (PFP)', SUM("50. PACQUIAO, MANNY PACMAN (PFP)") FROM raw.senate_25
    UNION ALL
    SELECT '51. PANGILINAN, KIKO (LP)', SUM("51. PANGILINAN, KIKO (LP)") FROM raw.senate_25
    UNION ALL
    SELECT '52. QUERUBIN,  ARIEL PORFIRIO (NP)', SUM("52. QUERUBIN,  ARIEL PORFIRIO (NP)") FROM raw.senate_25
    UNION ALL
    SELECT '53. QUIBOLOY, APOLLO (IND)', SUM("53. QUIBOLOY, APOLLO (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '54. RAMOS, DANILO (MKBYN)', SUM("54. RAMOS, DANILO (MKBYN)") FROM raw.senate_25
    UNION ALL
    SELECT '55. REVILLAME, WILLIE WIL (IND)', SUM("55. REVILLAME, WILLIE WIL (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '56. RODRIGUEZ, ATTY. VIC (IND)', SUM("56. RODRIGUEZ, ATTY. VIC (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '57. SAHIDULLA, NUR-ANA (IND)', SUM("57. SAHIDULLA, NUR-ANA (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '58. SALVADOR, PHILLIP IPE (PDPLBN)', SUM("58. SALVADOR, PHILLIP IPE (PDPLBN)") FROM raw.senate_25
    UNION ALL
    SELECT '59. SOTTO, TITO (NPC)', SUM("59. SOTTO, TITO (NPC)") FROM raw.senate_25
    UNION ALL
    SELECT '60. TAPADO, MICHAEL BONGBONG (PM)', SUM("60. TAPADO, MICHAEL BONGBONG (PM)") FROM raw.senate_25
    UNION ALL
    SELECT '61. TOLENTINO, FRANCIS TOL (PFP)', SUM("61. TOLENTINO, FRANCIS TOL (PFP)") FROM raw.senate_25
    UNION ALL
    SELECT '62. TULFO, BEN BITAG (IND)', SUM("62. TULFO, BEN BITAG (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '63. TULFO, ERWIN (LAKAS)', SUM("63. TULFO, ERWIN (LAKAS)") FROM raw.senate_25
    UNION ALL
    SELECT '64. VALBUENA, MAR MANIBELA (IND)', SUM("64. VALBUENA, MAR MANIBELA (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '65. VERCELES, LEANDRO (IND)', SUM("65. VERCELES, LEANDRO (IND)") FROM raw.senate_25
    UNION ALL
    SELECT '66. VILLAR, CAMILLE (NP)', SUM("66. VILLAR, CAMILLE (NP)") FROM raw.senate_25
) AS all_candidates
ORDER BY total_votes DESC
LIMIT 12;

-- turnout percentage per region
SELECT
	region
    , SUM("registeredVoters") AS registered
    , SUM("actualVoters") AS actual
    , ROUND(SUM("actualVoters")::numeric / NULLIF(SUM("registeredVoters"), 0) * 100, 2) AS turnout_pct
FROM raw.senate_25
GROUP BY region
ORDER BY turnout_pct DESC;


-- =============================================
-- PARTYLIST_25 EXPLORATION QUERIES
-- =============================================

-- Verifying row count (expected: 92,822)
SELECT COUNT(*) AS total_rows
FROM raw.partylist_25;

-- Unique geographic counts (expected to match senate_25)
SELECT
    COUNT(DISTINCT region)       AS regions
    , COUNT(DISTINCT province)   AS provinces
    , COUNT(DISTINCT municipality) AS municipalities
    , COUNT(DISTINCT barangay)   AS barangays
FROM raw.partylist_25;

-- Number of precincts per region
SELECT
    region
    , COUNT(*) AS precinct_count
FROM raw.partylist_25
GROUP BY region
ORDER BY precinct_count DESC;

-- Turnout percentage per region
SELECT
    region
    , SUM("registeredVoters") AS registered
    , SUM("actualVoters")     AS actual
    , ROUND(
        SUM("actualVoters")::numeric
        / NULLIF(SUM("registeredVoters"), 0) * 100
      , 2)                    AS turnout_pct
FROM raw.partylist_25
GROUP BY region
ORDER BY turnout_pct DESC;

-- Top party lists by vote: see notebooks/partylist_25/03_partylist_analysis.py
-- Wide format makes this impractical in raw SQL. Will be modeled in dbt Phase 3.
