"""
Main script to initialize logger and server
"""
import minio
from fastapi import Query
import os
from minio import Minio
import uvicorn


from fastapi import FastAPI, status, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from influxdb_client import InfluxDBClient
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.helpers.config_helper import props
from app.routers.user import router as user_router
from rad.getdata import retrive_from_influx
from getminio import read_minio_object
from retrive import get_data_from_influxdb
from datetime import datetime
from fastapi.responses import JSONResponse

from pydantic import BaseModel  # Make sure to include this import


__author__ = "Dinesh Sinnarasse"
__copyright__ = "Copyright 2023, Enterprise Minds"
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Enterprise Minds"
__status__ = "Development"


def get_application() -> FastAPI:
    """
    Initialize the application server with logger
    :return: fastApi app
    """
    application = FastAPI(title="Anomaly-detection", debug=True)
    return application


app = get_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


class MinioEventPayload(BaseModel):
    EventName: str
    Key: str
    Records: list


def init_database_connection():
    """
    Mehtod to initiate DBConnection
    :return: database_object
    """
    try:
        connection_url = props.get_properties("database", "connection_url")
        db_name = props.get_properties("database", "db_name")
        influx_token = props.get_influx_token()
        influx_org = props.get_influx_org()
        client = InfluxDBClient(
            connection_url, influx_token, influx_org)
    except Exception:
        raise Exception("Database connection error")
    return client


@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': 'Everything OK!'}


@app.get("/download-hari")
async def download_bucket_object():
    try:
        influx_client = init_database_connection()

        read_minio_object(
            influx_client=influx_client)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#tis is added by L.balasrinivasan
@app.post("/download")
async def download_bucket_object(payload: MinioEventPayload):

    #local_file_path = f"D:\\Anomaly\\Anomaly-detection\\{object_name}"
    try:
        influx_client = init_database_connection()
        object_name = payload.Key 
        bucket_name="dev"
        object_name = object_name[4:]

        read_minio_object(bucket_name,object_name,
                          influx_client=influx_client)
        # Call perform_insertdata with the file path
        # perform_insertdata(file_path=local_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#this is for priyadharshini
@app.get("/data/{start_time}/{end_time}/{interval}")
def get_data(start_time: datetime, end_time: datetime, interval: str):
    try:
        print(f"Received request: start_time={start_time}, end_time={end_time}, interval={interval}")
        # Pass the parameters to the function in the data_handler module
        data = get_data_from_influxdb(start_time, end_time, interval)
        return {"data": data}
    except Exception as e:
        # Print the exception for debugging purposes
        print("Error fetching data:", e)
        # Return an error response
        return JSONResponse(status_code=500, content={"error": "Failed to fetch data from InfluxDB."})

@app.get("/getdata")
async def get_datafrom_influx():
    try:
        print("started")
        retrive_from_influx()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Read server connection details
    host = props.get_properties("connection", "host")
    port = props.get_properties("connection", "port")

    uvicorn.run(app, host=host, port=int(port))
