-- =========================================================
-- Redshift Permissions
-- =========================================================
-- Placeholder IAM roles used for local/demo deployments.
-- Replace with your own IAM roles before execution.
--
-- Roles:
-- IAMR:part-search-lambda-role
-- IAMR:redshift-etl-lambda-role
-- IAMR:geocode-site-address-role
-- =========================================================


-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES
TO "IAMR:part-search-lambda-role";

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, UPDATE ON TABLES
TO "IAMR:geocode-site-address-role";

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES
TO "IAMR:redshift-etl-lambda-role";


-- Schema access
GRANT USAGE ON SCHEMA public
TO "IAMR:part-search-lambda-role";

GRANT USAGE ON SCHEMA public
TO "IAMR:redshift-etl-lambda-role";

GRANT USAGE ON SCHEMA public
TO "IAMR:geocode-site-address-role";


-- Search Lambda permissions
GRANT SELECT ON TABLE fact_parts_by_site
TO "IAMR:part-search-lambda-role";

GRANT SELECT ON TABLE dim_sites
TO "IAMR:part-search-lambda-role";

GRANT SELECT ON TABLE dim_planners_by_site
TO "IAMR:part-search-lambda-role";

GRANT ALL ON TABLE search_part_distance_result
TO "IAMR:part-search-lambda-role";


-- Geocode Lambda permissions
GRANT SELECT, UPDATE ON TABLE dim_sites
TO "IAMR:geocode-site-address-role";


-- ETL Lambda permissions
GRANT ALL ON TABLE stg_planners_by_site
TO "IAMR:redshift-etl-lambda-role";

GRANT ALL ON TABLE stg_parts_by_site
TO "IAMR:redshift-etl-lambda-role";

GRANT ALL ON TABLE stg_site_addresses
TO "IAMR:redshift-etl-lambda-role";

GRANT ALL ON TABLE fact_parts_by_site
TO "IAMR:redshift-etl-lambda-role";

GRANT ALL ON TABLE dim_planners_by_site
TO "IAMR:redshift-etl-lambda-role";

GRANT ALL ON TABLE dim_sites
TO "IAMR:redshift-etl-lambda-role";


-- Stored procedure access
GRANT EXECUTE ON PROCEDURE sp_part_transfer_pipeline()
TO "IAMR:redshift-etl-lambda-role";

GRANT EXECUTE ON PROCEDURE sp_search_part_distance(VARCHAR, VARCHAR)
TO "IAMR:part-search-lambda-role";


-- Optional broad permissions for development environments
GRANT ALL ON ALL TABLES IN SCHEMA public
TO "IAMR:redshift-etl-lambda-role";

GRANT SELECT, UPDATE ON ALL TABLES IN SCHEMA public
TO "IAMR:geocode-site-address-role";

GRANT SELECT ON ALL TABLES IN SCHEMA public
TO "IAMR:part-search-lambda-role";