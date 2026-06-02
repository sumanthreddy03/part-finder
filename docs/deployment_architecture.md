**Deployment Architecture**



!\[Deployment Architecture](screenshots/deployment\_architecture.png)



**Overview**



Part Finder is an AWS-based inventory search solution that allows users to search part availability across sites using either a Flask web interface or a Slack bot.

The application uses Amazon ECS for hosting the Flask application, AWS Lambda for backend processing, Amazon Redshift for data storage and search logic, and Amazon S3 for source file ingestion. This diagram illustrates the application deployment workflow, data refresh pipeline, and geocoding process.



**Search Workflow**



The search workflow begins from either the Flask UI or Slack.



User

&#x20;   ↓

Flask UI OR Slack App

&#x20;   ↓

slack\_bot\_handler Lambda (Slack only)

&#x20;   ↓

Flask Application hosted on ECS

&#x20;   ↓

part\_search\_service.py

&#x20;   ↓

API Gateway Search Endpoint

&#x20;   ↓

search\_part\_lambda

&#x20;   ↓

sp\_search\_part\_distance()

&#x20;   ↓

Amazon Redshift

&#x20;   ↓

search\_part\_distance\_result

&#x20;   ↓

Results returned to Flask

&#x20;   ↓

Results displayed in UI or Slack





**Flask Search Flow**



Browser User

&#x20;   ↓

Flask UI

&#x20;   ↓

/search-ui

&#x20;   ↓

part\_search\_service.py

&#x20;   ↓

API Gateway

&#x20;   ↓

search\_part\_lambda

&#x20;   ↓

Redshift Stored Procedure

&#x20;   ↓

Results returned to Flask

&#x20;   ↓

HTML Table Display





**Slack Search Flow**



Slack User

&#x20;   ↓

Slack App

&#x20;   ↓

API Gateway

&#x20;   ↓

slack\_bot\_handler Lambda

&#x20;   ↓

Async Lambda Invocation

&#x20;   ↓

Flask API Endpoint

&#x20;   ↓

search\_part\_lambda

&#x20;   ↓

Redshift Stored Procedure

&#x20;   ↓

Results returned

&#x20;   ↓

Slack Message Posted Back





**Data Refresh Workflow**



Inventory, planner, and site data are refreshed automatically when source files are uploaded.



CSV Files

&#x20;   ↓

S3 Sync Service

&#x20;   ↓

Amazon S3

&#x20;   ↓

S3 Event Trigger

&#x20;   ↓

trigger\_redshift\_sp Lambda

&#x20;   ↓

sp\_part\_transfer\_pipeline()

&#x20;   ↓

Staging Tables

&#x20;   ↓

Dimension Tables

&#x20;   ↓

Fact Table





**Geocoding Workflow**



Site coordinates are maintained automatically after each pipeline refresh.



trigger\_redshift\_sp Lambda

&#x20;   ↓

geocode\_site\_address Lambda

&#x20;   ↓

AWS Location Service

&#x20;   ↓

Latitude / Longitude

&#x20;   ↓

dim\_sites





**ECS Deployment Workflow**



The Flask application is containerized using Docker and deployed on Amazon ECS.



Flask Application

&#x20;   ↓

Docker Image

&#x20;   ↓

Amazon ECR

&#x20;   ↓

Amazon ECS

&#x20;   ↓

Public Flask Endpoint





The ECS endpoint is referenced by YOUR\_WEBSITE\_API\_URL and is used by the Slack bot to retrieve search results.



**Core Components**



* Flask App            --> User interface and API consumer
* Amazon ECS           --> Hosts Flask application
* Amazon ECR           --> Stores Docker image
* Slack App            --> Slack user interface
* Slack Lambda         --> Processes Slack commands and mentions
* Search Lambda        --> Executes Redshift search logic
* ETL Lambda           --> Runs Redshift refresh pipeline
* Geocode Lambda       --> Updates site coordinates
* Amazon S3            --> Stores source CSV files
* Amazon Redshift      --> Stores inventory and search data
* AWS Location Service --> Geocodes site addresses





**Notes**



This repository uses:

* Sanitized sample data
* Placeholder AWS resources
* Placeholder IAM roles
* Placeholder URLs

Replace all placeholders before deployment.

