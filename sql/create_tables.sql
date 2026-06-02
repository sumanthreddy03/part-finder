--================================================================
-- Staging Tables
-- Raw data loaded from S3 before transformation.
--================================================================

DROP TABLE IF EXISTS stg_parts_by_site;
CREATE TABLE IF NOT EXISTS stg_parts_by_site (
    continent VARCHAR(500),
    region VARCHAR(500),
    bu VARCHAR(500),
    site VARCHAR(500),
    site_store VARCHAR(500),
    default_bin VARCHAR(500),
    apn VARCHAR(500),
    part_class VARCHAR(500),
    part_description VARCHAR(500),
    part_criticality VARCHAR(500),
    price_per_unit VARCHAR(500),
    inventory_units VARCHAR(500),
    uom VARCHAR(500),
    min_level VARCHAR(500),
    max_level VARCHAR(500),
    inventory_status VARCHAR(500),
    total_inventory_units_above_max VARCHAR(500),
    inventory_value VARCHAR(500),
    parts_installed VARCHAR(500),
    equipments VARCHAR(500),
    min_equipment_criticality VARCHAR(500),
    preferred_supplier_name VARCHAR(500),
    preferred_supplier_reference VARCHAR(500),
    preferred_manufacturer VARCHAR(500),
    preferred_manufacturer_part_number VARCHAR(500)
);

DROP TABLE IF EXISTS stg_site_addresses;
CREATE TABLE IF NOT EXISTS stg_site_addresses (
    name VARCHAR(500),
    type VARCHAR(500),
    address VARCHAR(500),
    Country VARCHAR(500),
    zip_code VARCHAR(500),
    status VARCHAR(500)
);

DROP TABLE IF EXISTS stg_planners_by_site;
CREATE TABLE IF NOT EXISTS stg_planners_by_site (
    user_id VARCHAR(500),
    description VARCHAR(500),
    home_organization VARCHAR(500),
    user_group VARCHAR(500),
    associated_supplier VARCHAR(500),
    department VARCHAR(500),
    e_mail_address VARCHAR(500),
    external_user_id VARCHAR(500),
    knet_integration_status VARCHAR(500),
    last_login_attempt VARCHAR(500),
    language VARCHAR(500),
    mobile VARCHAR(500),
    allow_lt_confirm_completion VARCHAR(500),
    allow_contains_search_in_dataspy_and_quick_filter VARCHAR(500),
    allow_viewing_audit_trail VARCHAR(500),
    locale VARCHAR(500),
    digital_work_app VARCHAR(500)
);


--================================================================
-- Dimension Tables
-- Reference data used by reporting and search workflows.
--================================================================

CREATE TABLE IF NOT EXISTS dim_sites (
    site_code VARCHAR(50),
    site_type VARCHAR(100),
    address VARCHAR(500),
    zip_code VARCHAR(50),
    status VARCHAR(100),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);


CREATE TABLE IF NOT EXISTS dim_planners_by_site (
    site_code VARCHAR(50),
    planner_name VARCHAR(200),
    alias VARCHAR(200),
    email VARCHAR(200)
);


--================================================================
-- Fact Tables
-- Inventory records used for part availability searches.
--================================================================

CREATE TABLE IF NOT EXISTS fact_parts_by_site (
    apn VARCHAR(200),
    site VARCHAR(50),
    part_description VARCHAR(1000),
    default_bin VARCHAR(200),
    inventory_units VARCHAR(200),
    min_level VARCHAR(100),
    max_level VARCHAR(100),
    inventory_status VARCHAR(200),
    total_inventory_units_above_max VARCHAR(200)
);

