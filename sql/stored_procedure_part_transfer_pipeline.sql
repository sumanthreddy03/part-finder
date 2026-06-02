-- =========================================================
-- Part Transfer Pipeline
-- =========================================================
-- Purpose:
-- Loads source files from S3 into staging tables and refreshes
-- the reporting tables used by the Part Finder application.
--
-- Workflow:
-- S3 Files-> Staging Tables-> Dimension Tables-> Fact Table

--NOTE:
-- Replace S3 paths and IAM role placeholders with your own
-- environment-specific values before deployment.
-- =========================================================

CREATE OR REPLACE PROCEDURE sp_part_transfer_pipeline()
LANGUAGE plpgsql
AS $$
BEGIN

    -- Clear staging tables before loading fresh source data
    TRUNCATE TABLE stg_planners_by_site;
    TRUNCATE TABLE stg_parts_by_site;
    TRUNCATE TABLE stg_site_addresses;

    -- Load planner source data from S3
    COPY stg_planners_by_site
    FROM 's3://your_s3_bucket_name/planners_by_site/planners_by_site_s3.csv'
    IAM_ROLE 'arn:aws:iam::<aws-account-id>:role/<redshift-copy-role-name>'
    CSV
    IGNOREHEADER 1
    EMPTYASNULL
    BLANKSASNULL;

    -- Load inventory source data from S3
    COPY stg_parts_by_site
    FROM 's3://your_s3_bucket_name/parts_by_site_s3/parts_by_site.csv'
    IAM_ROLE 'arn:aws:iam::<aws-account-id>:role/<redshift-copy-role-name>'
    CSV
    IGNOREHEADER 1
    EMPTYASNULL
    BLANKSASNULL;

    -- Load site address source data from S3
    COPY stg_site_addresses
    FROM 's3://your_s3_bucket_name/site_addresses/site_addresses_s3.csv'
    IAM_ROLE 'arn:aws:iam::<aws-account-id>:role/<redshift-copy-role-name>'
    CSV
    IGNOREHEADER 1
    EMPTYASNULL
    BLANKSASNULL;

    
-- Preserve existing coordinates before refreshing site data
DROP TABLE IF EXISTS tmp_dim_sites_old;

CREATE TEMP TABLE tmp_dim_sites_old AS
SELECT *
FROM dim_sites;

    -- Refresh site dimension
    DELETE FROM dim_sites;

    INSERT INTO dim_sites (
        site_code,
        site_type,
        address,
        zip_code,
        status,
        latitude,
        longitude
    )
    SELECT DISTINCT
        UPPER(TRIM(s.name)) AS site_code,
        TRIM(s.type) AS site_type,
        TRIM(s.address) AS address,
        TRIM(s.zip_code) AS zip_code,
        TRIM(s.status) AS status,
        prev.latitude,
        prev.longitude
    FROM stg_site_addresses s
    LEFT JOIN tmp_dim_sites_old prev
        ON UPPER(TRIM(s.name)) = prev.site_code
    WHERE s.name IS NOT NULL;

    -- Refresh planner dimension
    DELETE FROM dim_planners_by_site;

    INSERT INTO dim_planners_by_site (
        site_code,
        planner_name,
        alias,
        email
    )
    SELECT
        UPPER(TRIM(home_organization)) AS site_code,
        TRIM(description) AS planner_name,
        TRIM(external_user_id) AS alias,
        TRIM(user_id) AS email

    FROM stg_planners_by_site
    WHERE home_organization IS NOT NULL;
    
    -- Refresh inventory fact table
    DELETE FROM fact_parts_by_site;

    INSERT INTO fact_parts_by_site (
        apn,
        site,
        part_description,
        default_bin,
        inventory_units,
        min_level,
        max_level,
        inventory_status,
        total_inventory_units_above_max

    )
        SELECT
        TRIM(apn) AS apn,
        TRIM(site) AS site,
        TRIM(part_description) AS part_description,
        TRIM(default_bin) AS default_bin,
        TRIM(inventory_units) AS inventory_units,
        TRIM(min_level) AS min_level,
        TRIM(max_level) AS max_level,
        TRIM(inventory_status) AS inventory_status,
        TRIM(total_inventory_units_above_max) AS total_inventory_units_above_max

    FROM stg_parts_by_site
    WHERE Site IS NOT NULL;

END;
$$;