**IAM Permissions**

* This project uses separate IAM roles for each Lambda function.



**Part Search Lambda**

* Purpose: Execute Redshift search procedure.



AWS Permissions

* redshift-data:ExecuteStatement
* redshift-data:DescribeStatement
* redshift-data:GetStatementResult
* CloudWatch Logs permissions



Redshift Access

* SELECT on fact\_parts\_by\_site
* SELECT on dim\_sites
* SELECT on dim\_planners\_by\_site
* EXECUTE on sp\_search\_part\_distance()



**ETL Lambda**

* Purpose: Run ETL pipeline after S3 uploads.



AWS Permissions

* redshift-data:ExecuteStatement
* redshift-data:DescribeStatement
* lambda:InvokeFunction
* CloudWatch Logs permissions



Redshift Access

* ALL on staging tables
* ALL on fact/dimension tables
* EXECUTE on sp\_part\_transfer\_pipeline()



**Geocode Lambda**

* Purpose: Update site coordinates.



AWS Permissions

* geo:Geocode
* redshift-data:ExecuteStatement
* redshift-data:GetStatementResult
* CloudWatch Logs permissions



Redshift Access

* SELECT, UPDATE on dim\_sites



**Slack Bot Lambda**

* Purpose: Process Slack commands and app mentions.



AWS Permissions

* lambda:InvokeFunction
* CloudWatch Logs permissions



Environment Variables

* SLACK\_BOT\_TOKEN
* SLACK\_SIGNING\_SECRET
* YOUR\_WEBSITE\_API\_URL
* LAMBDA\_FUNCTION\_NAME



**Redshift COPY Role**

* Purpose: Allow Redshift to load files from S3.



AWS Permissions

* s3:GetObject
* s3:ListBucket



Placeholder ARN

* arn:aws:iam:::role/





See:

sql/grant\_permissions.sql

docs/setup\_steps.md

