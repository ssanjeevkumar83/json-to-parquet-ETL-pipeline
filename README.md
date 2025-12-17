# AWS Event-Driven ETL Pipeline Project

## Project Overview
This project demonstrates an end-to-end Data Engineering ETL pipeline using AWS serverless services. The pipeline is **event-driven**, meaning it automatically triggers execution whenever new data is uploaded to the source.

**Goal**: Ingest raw JSON orders data, transform it into a structured Parquet format, catalog it, and make it queryable using SQL.

## Architecture
**S3 (Source)** -> **AWS Lambda (Transform)** -> **S3 (Data Lake)** -> **AWS Glue (Catalog)** -> **Amazon Athena (Analyze)**

```
aws-etl-pipeline/
├── data/
│   └── orders.json          # Sample input data
├── lambda_function.py       # Main ETL logic
├── README.md                # Documentation
└── requirements.txt         # Dependencies (for local testing)
```

1.  **Ingest**: JSON files uploaded to S3 bucket (`incoming` folder).
2.  **Trigger**: S3 Event Notification triggers AWS Lambda.
3.  **Transform**: Lambda runs Python (Pandas) to:
    * Read the JSON file.
    * Flatten the nested structure.
    * Convert data to Parquet format.
    * Save the Parquet file to the `data_lake` folder in S3.
4.  **Catalog**: Lambda triggers an AWS Glue Crawler to update the Data Catalog.
5.  **Analyze**: Data is queried using Amazon Athena.

## Prerequisites
* AWS Account
* Basic Python & SQL knowledge
* IAM Roles with permissions for S3, Glue, and Lambda.

---

## Step-by-Step Setup Guide

### Step 1: S3 Bucket Setup
1.  Create a new S3 bucket (e.g., `sql-etl-project`).
2.  Create two folders inside:
    * `orders_json_incoming/` (For raw data)
    * `orders_parquet_datalake/` (For transformed data)

### Step 2: AWS Lambda Setup
1.  Create a Function:
    * **Runtime**: Python 3.x
    * **Architecture**: x86_64
2.  **Add Layers**:
    * Scroll to the bottom -> "Add a layer" -> "AWS layers".
    * Select `AWSSDKPandas-Python3x` (This installs Pandas and PyArrow).
3.  **Configuration**:
    * Increase **Timeout** to 30 seconds or 1 minute (Configuration -> General configuration).
4.  **Permissions (IAM)**:
    * Go to Configuration -> Permissions -> Click the execution role.
    * Attach policies: `AmazonS3FullAccess` and `AWSGlueServiceRole` (or create a custom inline policy for specific buckets/crawlers).

### Step 3: The ETL Code (Lambda)
* Copy the code from `lambda_function.py` in this repo into the Lambda code editor.
* **Logic**:
    * Extracts bucket name and file key from the trigger event.
    * Reads the JSON object using `boto3`.
    * Flattens the JSON list into a DataFrame.
    * Writes the DataFrame to a Parquet buffer.
    * Uploads the Parquet file back to S3.
    * Triggers the Glue Crawler.

### Step 4: Set Up S3 Trigger
1.  In the Lambda console, click **Add trigger**.
2.  Select **S3**.
3.  Choose your bucket.
4.  **Prefix**: `orders_json_incoming/` (Ensures only files in this folder trigger the pipeline).
5.  **Suffix**: `.json`.
6.  Click **Add**.

### Step 5: AWS Glue Crawler
1.  Go to AWS Glue -> Crawlers -> **Create crawler**.
2.  **Data Source**: Select S3 and browse to the `orders_parquet_datalake/` folder.
3.  **IAM Role**: Create a role with Glue permissions.
4.  **Target Database**: Create a new database (e.g., `etl_pipeline_db`).
5.  **Schedule**: Leave as "On demand".
6.  Save the crawler name (e.g., `pipeline_crawler`) and update it in your `lambda_function.py` variable.

### Step 6: Testing
1.  Upload `orders.json` to the `orders_json_incoming/` folder in S3.
2.  Check CloudWatch Logs for Lambda execution details.
3.  Verify a new `.parquet` file appears in `orders_parquet_datalake/`.
4.  Wait for the Glue Crawler to finish (status "Stopping").
5.  Go to **Amazon Athena**, select the database, and run:
    ```sql
    SELECT * FROM orders_parquet_datalake;
    ```

## Technologies Used
* **AWS S3**: Storage
* **AWS Lambda**: Compute & Transformation
* **AWS Glue**: Data Cataloging
* **Amazon Athena**: SQL Analytics

* **Python**: Pandas, Boto3

