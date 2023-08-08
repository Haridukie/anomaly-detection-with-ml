from fastapi import FastAPI
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables from the .env file
load_dotenv()

app = FastAPI(debug=True)  # Enable debug mode

# InfluxDB configuration
INFLUXDB_HOST = "10.0.0.106:8086"
#INFLUXDB_DATABASE = "dataset_tt"
INFLUXDB_ORG = "eminds"  # Replace with your actual InfluxDB organization
INFLUXDB_BUCKET = "dev"  # Replace with your actual InfluxDB bucket
INFLUXDB_TOKEN = "sIokMknLOBmfxMMrtkrMQTqImwd_wGnMH1-b6Hz_WDvuWp4-ysJ0Cl7UHpaRw-0SovIfMPXwcwmN8bd_HERnGA=="  # Replace with your actual InfluxDB token

def get_data_from_influxdb(start_time: datetime, end_time: datetime, aggregation: str):
    # Create the InfluxDB client with token-based authentication
    client = InfluxDBClient(
        url=f"http://{INFLUXDB_HOST}",
        token=INFLUXDB_TOKEN,
    )

    # Convert the time range to RFC3339 format
    start_time_rfc3339 = start_time.isoformat() + "Z"
    end_time_rfc3339 = end_time.isoformat() + "Z"

    # Fetch data from the measurement within the specified time range and aggregation
    query_api = client.query_api()
    query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: {start_time_rfc3339}, stop: {end_time_rfc3339}) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "dataset_tt") ' \
            f'|> aggregateWindow(every: {aggregation}, fn: mean, createEmpty: false)'

    result = query_api.query(org=INFLUXDB_ORG, query=query)

    # Extract the data from the query result
    data = []
    i = 1
    for table in result:
        for record in table.records:
            data.append({
                "id": i,
                "_point": f" Point {i}",
                "_value": record.values["_value"],
                "_time": record.values["_time"],
            })
            i += 1

    return data
