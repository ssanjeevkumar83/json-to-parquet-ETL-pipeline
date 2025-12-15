import json
import boto3
import pandas as pd
import io
from datetime import datetime

# Initialize Clients
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')

def flatten_data(data):
    """
    Flattens the nested JSON structure (Orders -> Items).
    Adjust keys based on your specific JSON structure.
    """
    flattened_records = []
    
    for order in data:
        # Extract order-level info
        order_id = order.get('order_id')
        date = order.get('date')
        customer_id = order.get('customer_id')
        
        # Iterate through items in the order
        # Assuming 'items' is the key for the list of products
        for item in order.get('items', []):
            record = {
                'order_id': order_id,
                'date': date,
                'customer_id': customer_id,
                'product_id': item.get('product_id'),
                'quantity': item.get('quantity'),
                'price': item.get('price')
            }
            flattened_records.append(record)
            
    return pd.DataFrame(flattened_records)

def lambda_handler(event, context):
    # 1. Get Bucket Name and Key from the Event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    print(f"Triggered by file: {file_key} in bucket: {bucket_name}")

    try:
        # 2. Read the JSON file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        data = json.loads(file_content)
        
        # 3. Process/Flatten Data
        df = flatten_data(data)
        print("Data flattened successfully. Preview:")
        print(df.head())
        
        # 4. Convert DataFrame to Parquet (In-memory buffer)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
        
        # 5. Define Output Path (Data Lake)
        # Generate a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_key = f"orders_parquet_datalake/orders_{timestamp}.parquet"
        
        # 6. Upload Parquet to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=parquet_buffer.getvalue()
        )
        print(f"Parquet file uploaded to: {output_key}")
        
        # 7. Trigger Glue Crawler
        # Replace 'pipeline_crawler' with your actual crawler name
        crawler_name = "pipeline_crawler" 
        glue_client.start_crawler(Name=crawler_name)
        print(f"Glue Crawler '{crawler_name}' started.")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Processing complete for {file_key}')
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing file: {str(e)}")
        }