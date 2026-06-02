-- =========================================================
-- Part Distance Search Procedure
-- =========================================================
-- Purpose:
-- Returns inventory availability for a given APN across sites,
-- sorted by distance from the input site.
--
-- Inputs:
--   p_apn              -> Part number to search
--   p_input_site_code  -> Home site used as distance origin
--
-- Output:
--   search_part_distance_result
-- =========================================================

CREATE OR REPLACE PROCEDURE sp_search_part_distance(
    IN p_apn VARCHAR(200),
    IN p_input_site_code VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Refresh result table for the current search request
    DROP TABLE IF EXISTS  search_part_distance_result;

    CREATE TABLE search_part_distance_result AS

    -- Aggregate planner information at the site level
    WITH planner_agg AS (
        SELECT
            UPPER(TRIM(site_code)) AS site_code,

            LISTAGG(DISTINCT planner_name, ', ')
            WITHIN GROUP (ORDER BY planner_name) AS planner_names,

            LISTAGG(DISTINCT alias, ', ')
            WITHIN GROUP (ORDER BY planner_name) AS planner_aliases,

            LISTAGG(DISTINCT email, ', ')
            WITHIN GROUP (ORDER BY planner_name) AS planner_emails

        FROM dim_planners_by_site
        GROUP BY UPPER(TRIM(site_code))
    )

    SELECT DISTINCT
        -- Part inventory details
        p.site,
        p.apn,
        p.part_description,
        p.default_bin,
        p.inventory_units,
        p.min_level,
        p.max_level,
        p.inventory_status,
        COALESCE(p.total_inventory_units_above_max,'0') AS total_inventory_units_above_max,

        -- Site planner information
        pl.planner_names,
        pl.planner_aliases,
        pl.planner_emails,

        -- Site location details
        s.address,
        s.zip_code,

        -- Great-circle distance calculation (miles)
        3958.7613 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(s.latitude - origin.latitude) / 2), 2)
                +
                COS(RADIANS(origin.latitude))
* COS(RADIANS(s.latitude))
* POWER(SIN(RADIANS(s.longitude - origin.longitude) / 2), 2)
            )
        ) AS distance_miles

    FROM fact_parts_by_site p

    LEFT JOIN planner_agg pl
        ON UPPER(TRIM(p.site)) = pl.site_code

    LEFT JOIN dim_sites s
        ON UPPER(TRIM(p.site)) = UPPER(TRIM(s.site_code))

    -- Home site used as the distance origin
    JOIN dim_sites origin
        ON UPPER(TRIM(origin.site_code)) = UPPER(TRIM(p_input_site_code))

    WHERE UPPER(TRIM(p.apn)) = UPPER(TRIM(p_apn))

      -- Exclude the originating site from results
      AND UPPER(TRIM(p.site)) <> UPPER(TRIM(p_input_site_code))

      -- Distance calculation requires valid coordinates
      AND s.latitude IS NOT NULL
      AND s.longitude IS NOT NULL
      AND origin.latitude IS NOT NULL
      AND origin.longitude IS NOT NULL

    --Closest sites first
    ORDER BY distance_miles ASC;

END;
$$;