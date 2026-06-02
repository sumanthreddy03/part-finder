**Architecture**



**!\[Part Finder Architecture](screenshots/architecture.png)**



**Overview**



Part Finder is an inventory search application that allows users to find available parts across multiple sites based on part number and home site location accessed through a web interface and Slack integration. The system combines Amazon S3, AWS Lambda, Amazon Redshift, Amazon ECS, and Slack to provide inventory visibility and distance-based search capabilities.

High-Level Architecture



**Data Pipeline Architecture**



Source CSV Files

&#x20;       │

&#x20;       ▼

&#x20;  Amazon S3

&#x20;       │

&#x20;       ▼

trigger\_redshift\_sp

&#x20;     Lambda

&#x20;       │

&#x20;       ▼

sp\_part\_transfer\_pipeline

&#x20;       │

&#x20;       ▼

Staging Tables

&#x20;       │

&#x20;       ▼

Dimension Tables

&#x20;       │

&#x20;       ▼

Fact Table

&#x20;       │

&#x20;       ▼

Search Ready Data





**Geocoding Architecture**



dim\_sites

&#x20;   │

&#x20;   ▼

Missing Coordinates

&#x20;   │

&#x20;   ▼

geocode\_site\_address

&#x20;       Lambda

&#x20;   │

&#x20;   ▼

AWS Location Service

&#x20;   │

&#x20;   ▼

Latitude / Longitude

&#x20;   │

&#x20;   ▼

dim\_sites Update





**Search Architecture**



Part Number + Home Site

&#x20;           │

&#x20;           ▼

sp\_search\_part\_distance()

&#x20;           │

&#x20;           ▼

Inventory Lookup

&#x20;           │

&#x20;           ▼

Distance Calculation

&#x20;           │

&#x20;           ▼

Planner Lookup

&#x20;           │

&#x20;           ▼

Sorted Results



**Core AWS Services**



* Amazon ECS           --> Hosts Flask application
* Amazon ECR           --> Stores Docker images
* AWS Lambda           --> Executes backend workflows
* Amazon S3            --> Stores source CSV files
* Amazon Redshift      --> Stores inventory and planner data
* API Gateway          --> Exposes Lambda endpoints
* AWS Location Service --> Geocodes site addresses
* Slack App            --> User-facing chat interface





**Design Goals**



* Automated inventory data refresh
* Distance-based site search
* Slack and web-based access
* Serverless backend processing
* Containerized application deployment
* Separation of ETL, search, and geocoding workflows





**Notes**



This repository uses:

* Sanitized sample data
* Placeholder AWS resources
* Placeholder IAM roles
* Placeholder URLs

Replace all placeholders before deployment.

