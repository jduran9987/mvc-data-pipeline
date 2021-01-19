# NYC Motor Vehicle Collision Data
Automating the process of downloading API data.

## Overview

This simple data project attempts to show how we can automate the process of fetching data off of a public api.
The business use case for this project is obvious: we do not want to spend resources manually downloading data 
and performing the necessary housekeeping to prevent the unavoidable errors that comes with the human manual 
process.

We will utilize the NYC Opendata API to access data that describe motor vehicle collisions.  This is a free and open
public datasets so no access keys or credentials are needed.  

## Tools
* Docker
* Airflow
* Bash
* Python

## Setup
Begin by cloning this repository into your project directory.

`$ git clone https://github.com/jduran9987/mvc-data-pipeline.git`

Navigate to the DAG code at /dags/nyc_collisions_pipeline.py and update the start_date parameter in the DAG object
to the desired value. 

Finally, start up the containers with docker compose 

`$ docker-compose up -d`

## Airflow Webserver
In your browser, go to `http://localhost:8080` and turn on the nyc_collisions_pipeline DAG to begin triggering the tasks.

## Tutorial
Please visit my blog for a step-by-step tutorial for this project at https://duran9987.medium.com/lets-build-an-elt-pipeline-part-i-introduction-fd40a8a81aa5
