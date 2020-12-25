# Airflow modules
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.sensors.http_sensor import HttpSensor

# Python libraries
from datetime import datetime 


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

# Define the dependencies 
is_collisions_api_available >> fetch_collisions_data
