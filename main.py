#import asyncio
#import pika
#import pika.adapters.asyncio_connection
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import FileResponse
from prometheus_client import Counter, Gauge, generate_latest
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
import os
import time
import logging
from pythonjsonlogger.json import JsonFormatter

# Application logging setup
#logger = logging.getLogger()
#logger.setLevel(logging.INFO)

from utils.logging import logger
from utils.middleware import LogMiddleware

# FastAPI app setup with Swagger docs enabled
app = FastAPI(title="File Download Service", description="A FastAPI service for managing file downloads and logging", version="1.0")
app.add_middleware(LogMiddleware)
logging.info("FastAPI APP created, Swagger enabled at /docs URL")

# Prometheus Metrics
DOWNLOAD_COUNTER = Counter("file_downloads", "Count of file downloads", ["filename"])
ERROR_COUNTER = Counter("errors", "Count of errors", ["type"])
RABBITMQ_MESSAGE_COUNTER = Counter("rabbitmq_messages", "Count of RabbitMQ messages received")

# Database setup
DATABASE_URL = "sqlite:///./downloads.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DownloadLog(Base):
    __tablename__ = "download_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50))
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    file_size = Column(Integer)
    transfer_time = Column(Float)
    throughput_mbps = Column(Float)
    file_age_seconds = Column(Float)

class FilenameRegistry(Base):
    __tablename__ = "filenames"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

STATIC_DIR = "./static"


@app.get("/download/{filename}")
def download_file(filename: str, request: Request):
    """
    Allows a client to download a file, if it is available.  Downloads are logged.  If file is not available
    let the user know if it is a file we had at one point that has since been deleted.

    Args:
        filename (str): the name of the requested file

    Returns:
        FileResponse (the file, if it is available)

    Raises:
        HttpException: if the file is not available

    """
    db = SessionLocal()
    file_path = os.path.join(STATIC_DIR, filename)
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        file_mod_time = os.path.getmtime(file_path)
        file_age_seconds = time.time() - file_mod_time
        start_time = time.time()

        response = FileResponse(file_path, filename=filename)

        transfer_time = time.time() - start_time
        throughput_mbps = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0

        db.add(DownloadLog(
            filename=filename,
            status='downloaded',
            ip_address=ip_address,
            user_agent=user_agent,
            file_size=file_size,
            transfer_time=transfer_time,
            throughput_mbps=throughput_mbps,
            file_age_seconds=file_age_seconds
        ))
        DOWNLOAD_COUNTER.labels(filename=filename).inc()
        db.commit()
        db.close()
        return response
    else:
        history = db.query(DownloadLog).filter(DownloadLog.filename == filename).all()
        db.add(DownloadLog(filename=filename, status='not found', ip_address=ip_address, user_agent=user_agent))
        db.commit()
        db.close()

        if history:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found, but was previously downloaded.")
        else:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

@app.get("/metrics")
async def metrics():
    logger.info("metrics")
    return generate_latest()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
