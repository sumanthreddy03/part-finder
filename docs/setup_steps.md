Setup Steps



1. Clone Repository



git clone <your-repository-url>
cd part-finder





2. Create AWS Resources



Create the following AWS resources:

Amazon S3 Bucket
Amazon Redshift Serverless Workgroup
Amazon Redshift Database
Amazon ECR Repository
Amazon ECS Service
AWS Lambda Functions
API Gateway
Slack App (Optional)





3. Configure IAM Roles



Create IAM roles for:

Part Search Lambda
ETL Lambda
Geocode Lambda
Slack Bot Lambda
Redshift COPY operations
ECS Task Execution



See:

docs/iam_permissions.md





4. Create Redshift Objects



Run the SQL scripts in the following order:

sql/create_tables.sql
sql/stored_procedure_calculate_distance.sql
sql/stored_procedure_part_transfer_pipeline.sql
sql/grant_permissions.sql





5. Upload Sample Data to S3



Upload sample CSV files to the configured S3 bucket.
data_samples/sample_parts.csv
data_samples/sample_planners.csv
data_samples/sample_site_addresses.csv



The S3 folder structure should match the paths referenced inside:

sql/stored_procedure_part_transfer_pipeline.sql





6. Configure Environment Variables



Copy .env.example to .env

Replace all placeholder values with your own AWS resources.



Required variables include:

SEARCH_API_URL
S3_BUCKET_NAME
REDSHIFT_WORKGROUP
REDSHIFT_DATABASE
STORED_PROCEDURE
GEOCODE_LAMBDA_NAME
YOUR_WEBSITE_API_URL
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
LAMBDA_FUNCTION_NAME





7. Deploy Lambda Functions



Deploy the following Lambda functions:

lambda/search_part_lambda.py
lambda/trigger_redshift_sp.py
lambda/geocode_site_address.py
lambda/slack_bot_handler.py

Configure environment variables for each Lambda function.





8. Build and Push Docker Image



Build the Flask application image: docker build -t part-finder-app .

Tag the image: docker tag part-finder-app:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/part-finder-app:latest

Push the image: docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/part-finder-app:latest





9. Deploy Flask Application to ECS



Create or update an ECS service using the Docker image pushed to ECR.

The Flask application exposes: POST /search-part

This endpoint is used by the Slack bot and UI.

Example placeholder: https://your-ecs-service-url/search-part





10. Configure Slack App (Optional)



Import docs/slack_app_manifest.json



Update the Slack request URLs:

* https://your-api-gateway-url/events
* https://your-api-gateway-url/interactions



Configure Slack Lambda environment variables:

SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
YOUR_WEBSITE_API_URL
LAMBDA_FUNCTION_NAME



Set YOUR_WEBSITE_API_URL=https://your-ecs-service-url/search-part





11. Test ETL Pipeline



Upload a file to S3.

Expected workflow:

S3 Upload --> trigger_redshift_sp Lambda --> sp_part_transfer_pipeline --> dim/fact table refresh --> geocode_site_address Lambda --> Coordinate updates



12. Test Part Search



Test using Flask UI http://localhost or ECS URL.

API Endpoint: POST /search-part

Example payload:{"apn": "PART1001", "input_site_code": "SITE_A"}



Slack Command

/find PART1001 SITE_A



Slack Mention

@PART_FINDER PART1001 SITE_A





13. Validation Queries



Run sql/validation.sql to verify

Site coordinates
Stored procedure execution
Search results



Note:

This repository uses:

Sanitized sample data

Placeholder AWS resources

Placeholder IAM roles

Placeholder URLs

Replace all placeholders before deployment.

