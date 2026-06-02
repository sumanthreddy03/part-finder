-- =========================================================
-- Validation Queries
-- =========================================================
-- Quick checks used during development and testing.
-- =========================================================

-- Validate latitude/longitude ranges
SELECT * 
from dim_sites
WHERE latitude NOT BETWEEN -90 AND 90
OR longitude NOT BETWEEN -180 AND 180;

-- Test distance search procedure
CALL sp_search_part_distance('<input_part_number>','<input_site_code>');

-- Review generated search results
SELECT * 
FROM search_part_distance_result
ORDER BY distance_miles ASC;


