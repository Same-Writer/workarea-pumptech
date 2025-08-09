#!/usr/bin/env python3
"""
InfluxDB Writer Script

Connects to a dockerized InfluxDB instance and writes dummy data
with timestamps and random integers once per second.
"""

import logging
import os
import random
import time
from datetime import datetime
from typing import Optional

try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    print("ERROR: influxdb-client not installed. Run: uv add influxdb-client")
    exit(1)


# Load configuration from environment variables
def load_env_file(filepath: str = ".env"):
    """Load environment variables from .env file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


# Load .env file if it exists
load_env_file()

# Configuration from environment variables with fallbacks
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8087")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-admin-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myorg")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "mybucket")

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfluxWriter:
    """Handles writing data to InfluxDB."""

    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None

    def connect(self) -> bool:
        """Connect to InfluxDB and initialize write API."""
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

            # Test connection
            ready = self.client.ready()
            if not ready:
                logger.error("InfluxDB is not ready")
                return False

            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logger.info("Successfully connected to InfluxDB")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            return False

    def write_dummy_data(self) -> bool:
        """Write a dummy data point with timestamp and random integer."""
        if not self.write_api:
            logger.error("Write API not initialized")
            return False

        try:
            # Generate random data
            random_value = random.randint(1, 100)
            temperature = random.uniform(18.0, 25.0)  # Random temperature
            humidity = random.uniform(40.0, 70.0)  # Random humidity

            # Create data points
            points = [
                Point("sensors")
                .tag("location", "office")
                .tag("sensor_id", "temp_001")
                .field("value", random_value)
                .field("temperature", round(temperature, 2))
                .field("humidity", round(humidity, 2))
                .time(datetime.utcnow()),
                Point("system_metrics")
                .tag("host", "server01")
                .field("cpu_usage", random.uniform(10.0, 90.0))
                .field("memory_usage", random.uniform(30.0, 80.0))
                .field("random_int", random_value)
                .time(datetime.utcnow()),
            ]

            # Write points to InfluxDB
            self.write_api.write(bucket=self.bucket, record=points)

            logger.info(
                f"Written data: random_value={random_value}, "
                f"temp={round(temperature, 2)}, "
                f"humidity={round(humidity, 2)}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to write data: {e}")
            return False

    def close(self):
        """Close the InfluxDB connection."""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")


def wait_for_influxdb(writer: InfluxWriter, max_retries: int = 30) -> bool:
    """Wait for InfluxDB to be ready with retries."""
    logger.info("Waiting for InfluxDB to be ready...")

    for attempt in range(max_retries):
        if writer.connect():
            return True

        logger.info(
            f"Attempt {attempt + 1}/{max_retries} failed, retrying in 2 seconds..."
        )
        time.sleep(2)

    logger.error("InfluxDB failed to become ready after maximum retries")
    return False


def main():
    """Main function to run the data writer."""
    logger.info("Starting InfluxDB Writer")

    # Initialize writer
    writer = InfluxWriter(INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET)

    # Wait for InfluxDB to be ready
    if not wait_for_influxdb(writer):
        logger.error("Could not connect to InfluxDB. Make sure it's running.")
        return

    try:
        logger.info("Starting to write data every second. Press Ctrl+C to stop.")

        while True:
            success = writer.write_dummy_data()
            if not success:
                logger.warning("Failed to write data, continuing...")

            time.sleep(1)  # Write once per second

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    finally:
        writer.close()
        logger.info("Writer stopped")


if __name__ == "__main__":
    main()
