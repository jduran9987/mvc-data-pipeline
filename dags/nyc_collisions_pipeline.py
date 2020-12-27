# Airflow modules
from dags.custom.operators import S3ToRedshiftOperator
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator 
from airflow.hooks.S3_hool import S3Hook 
from airflow.sensors.http_sensor import HttpSensor

# Custom operators
from custom.operators import S3ToRedshfitOperator

# Python libraries
from datetime import datetime 
import os 

# Helper functions 
def s3_hook(filename, key, bucket_name=os.environ.get("S3_BUCKET_NAME")):
    """
    Helper function to load a file into an S3 bucket.
    :param str filename: relative path of file to be uplaoded to S3
    :param str key: filename to be insterted into the target S3 bucket
    :param str bucket_name: name of S3 bucket
    """
    
    hook = S3Hook('s3_connection')
    hook.load_file(filename, key, bucket_name)


# Initiate our dag definition
dag = DAG(
    dag_id="nyc_collisions_pipeline",
    start_date=datetime(2020, 12, 19),
    schedule_interval="@daily"
)

# Check if collisions api has data for a given date
is_collisions_api_available = HttpSensor(
    task_id="is_collisions_api_available",
    method="GET",
    http_conn_id="nyc_collisions_api",
    endpoint="resource/h9gi-nx95.json?crash_date={{ ds }}",
    response_check=lambda response: "crash_date" in response.text,
    poke_interval=5,
    timeout=20,
    dag=dag
)

# Download collisions data for a given date
fetch_collisions_data = BashOperator(
    task_id="fetch_collisions_data",
    bash_command="curl -o /usr/local/airflow/data/{{ ds }}.json \
        --request GET \
        --url https://data.cityofnewyork.us/resource/h9gi-nx95.json?crash_date={{ ds }}",
    dag=dag 
)

# Upload collisions file into S3
upload_file_to_s3 = PythonOperator(
    task_id="upload_file_to_s3",
    python_callable=upload_file_to_s3,
    op_kwargs={
        "filename": "./data/{{ ds }}.json",
        "key": "{{ ds }}.json"
    },
    dag=dag
)

# Transfer collisions data from S3 to Redshift
transfer_to_redshift = S3ToRedshiftOperator(
    task_id="transfer_to_redshift",
    redshift_conn_id="redshift_connection",
    table=os.environ.get("REDSHIFT_TABLE_NAME"),
    s3_bucket=os.environ.get("S3_BUCKET_NAME"),
    s3_prefix="{{ ds_nodash }}.json",
    schema=os.environ.get("REDSHIFT_SCHEMA_NAME"),
    aws_conn_id="s3_connection",
    dag=dag
)

# Define the dependencies 
is_collisions_api_available >> fetch_collisions_data >> upload_file_to_s3 >> transfer_to_redshift
