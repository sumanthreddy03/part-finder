import boto3
import os
import json

# AWS service clients
redshift = boto3.client("redshift-data")
lambda_client = boto3.client("lambda")

# Environment configuration
# See .env.example for required values
REDSHIFT_WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
REDSHIFT_DATABASE = os.environ["REDSHIFT_DATABASE"]
STORED_PROCEDURE = os.environ["STORED_PROCEDURE"]
GEOCODE_LAMBDA_NAME=os.environ["GEOCODE_LAMBDA_NAME"]

def lambda_handler(event, context):
    print("S3 event received:")
    print(event)

    # Run ETL stored procedure after s3 file upload
    sql = f"CALL {STORED_PROCEDURE}();"

    response = redshift.execute_statement(
        WorkgroupName=REDSHIFT_WORKGROUP,
        Database=REDSHIFT_DATABASE,
        Sql=sql
    )

    # WAIT until Redshift stored procedure finishes
    statement_id = response["Id"]

    # Wait for the Redshift pipeline to finish
    while True:
        status = redshift.describe_statement(Id=statement_id)

        if status["Status"] == "FINISHED":
            break

        elif status["Status"] in ["FAILED", "ABORTED"]:
            raise Exception(status)

    # CALL GEOCODE LAMBDA/ Refresh site coordinates after pipeline completion
    lambda_client.invoke(
        FunctionName=GEOCODE_LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({
            "source": "redshift_pipeline_complete"
        })
    )

    return {
        "statusCode": 200,
        "message": "Pipeline + geocoding completed",
        "query_id": statement_id
    }