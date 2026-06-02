import boto3
import json
import os
import time

#Redshift Data API client
redshift = boto3.client("redshift-data")

#Environment configuration
#see .env.example for required values
REDSHIFT_WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
REDSHIFT_DATABASE = os.environ["REDSHIFT_DATABASE"]


def wait_for_statement(statement_id):
    #wait until Redshift finishes running the submitted SQL
    while True:
        status = redshift.describe_statement(Id=statement_id)

        if status["Status"] == "FINISHED":
            return status

        if status["Status"] in ["FAILED", "ABORTED"]:
            raise Exception(status)

        time.sleep(1)


def get_value(field):
    #Convert Redshift Data API field types into normal python values
    if "stringValue" in field:
        return field["stringValue"]
    if "longValue" in field:
        return field["longValue"]
    if "doubleValue" in field:
        return field["doubleValue"]
    if "booleanValue" in field:
        return field["booleanValue"]
    if field.get("isNull"):
        return None
    return None


def lambda_handler(event, context):
    try:
        #Parse API Gateway request body
        body = json.loads(event.get("body", "{}"))

        apn = body.get("apn")
        input_site_code = body.get("input_site_code")

        if not apn or not input_site_code:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "apn and input_site_code are required"
                })
            }

        # Call stored procedure that performs APN/Site distance search
        call_sql = f"""
            CALL sp_search_part_distance('{apn}', '{input_site_code}');
        """

        call_response = redshift.execute_statement(
            WorkgroupName=REDSHIFT_WORKGROUP,
            Database=REDSHIFT_DATABASE,
            Sql=call_sql
        )

        wait_for_statement(call_response["Id"])

        # Read the result table populated by the stored procedure
        select_sql = """
            SELECT *
            FROM search_part_distance_result
            ORDER BY distance_miles ASC
            LIMIT 20;
        """

        select_response = redshift.execute_statement(
            WorkgroupName=REDSHIFT_WORKGROUP,
            Database=REDSHIFT_DATABASE,
            Sql=select_sql
        )

        wait_for_statement(select_response["Id"])

        result = redshift.get_statement_result(Id=select_response["Id"])

        columns = [col["name"] for col in result["ColumnMetadata"]]

        # Convert Redshift records into list of dictionaries
        rows = []
        for record in result["Records"]:
            row_data = {}
            for i, field in enumerate(record):
                row_data[columns[i]] = get_value(field)
            rows.append(row_data)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "apn": apn,
                "input_site_code": input_site_code,
                "count": len(rows),
                "results": rows
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }