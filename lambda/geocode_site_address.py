import boto3
import json
import os
import time

# AWS clients
geo = boto3.client("geo-places")
redshift = boto3.client("redshift-data")

# Redshift connection settings
REDSHIFT_WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
REDSHIFT_DATABASE = os.environ["REDSHIFT_DATABASE"]

def wait_for_statement(statement_id):
    # Poll Redshift until query finishes
    while True:
        status = redshift.describe_statement(Id=statement_id)

        if status["Status"] == "FINISHED":
            return status

        if status["Status"] in ["FAILED", "ABORTED"]:
            raise Exception(status)

        time.sleep(1)

def geocode_address(address):
    # Convert a site address into latitude/longitude coordinates
    response = geo.geocode(
        QueryText=address,
        MaxResults=1
    )

    results = response.get("ResultItems", [])

    if not results:
        return None, None

    position = results[0]["Position"]

    longitude = position[0]
    latitude = position[1]

    return latitude, longitude

def lambda_handler(event, context):

    # Find sites that do not yet have coordinates
    response = redshift.execute_statement(
        WorkgroupName=REDSHIFT_WORKGROUP,
        Database=REDSHIFT_DATABASE,
        Sql="""
            SELECT site_code, address, zip_code
            FROM dim_sites
            WHERE latitude IS NULL
               OR longitude IS NULL
        """
    )

    statement_id = response["Id"]
    wait_for_statement(statement_id)

    results = redshift.get_statement_result(Id=statement_id)
    rows = results["Records"]

    updated_count = 0
    no_result_count = 0

    # Geocode each site and update Redshift
    for row in rows:
        site_code = row[0].get("stringValue", "")
        address = row[1].get("stringValue", "")
        zip_code = row[2].get("stringValue", "")

        if not site_code or not address:
            continue

        full_address = f"{address}, {zip_code}, USA"

        print("Geocoding:", site_code, full_address)

        lat, lon = geocode_address(full_address)

        print("Geocode result:", site_code, lat, lon)

        if lat is None or lon is None:
            no_result_count += 1
            continue

        update_sql = f"""
            UPDATE dim_sites
            SET latitude = {lat},
                longitude = {lon}
            WHERE UPPER(TRIM(site_code)) = UPPER(TRIM('{site_code}'))
        """

        update_response = redshift.execute_statement(
            WorkgroupName=REDSHIFT_WORKGROUP,
            Database=REDSHIFT_DATABASE,
            Sql=update_sql
        )

        wait_for_statement(update_response["Id"])
        updated_count += 1

    #Return summary metrics for monitoring and troubleshooting
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Geocoding completed",
            "rows_checked": len(rows),
            "updated_count": updated_count,
            "no_result_count": no_result_count
        })
    }