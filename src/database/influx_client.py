"""
InfluxDB client for the PumpTech system.

Refactored and improved version of the original influx-writer.py
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

try:
    from influxdb_client import InfluxDBClient as InfluxClient
    from influxdb_client import Point
    from influxdb_client.client.exceptions import InfluxDBError
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    print("ERROR: influxdb-client not installed. Run: uv add influxdb-client")
    exit(1)

from ..config import get_settings
from .models import AlarmEvent, PumpReading, SensorReading, SystemMetric

logger = logging.getLogger(__name__)


class InfluxDBClient:
    """Enhanced InfluxDB client with better error handling and data models."""

    def __init__(self, settings: Any = None):
        """Initialize the InfluxDB client."""
        if settings is None:
            settings = get_settings()

        self.settings = settings.influxdb
        self.client: Optional[InfluxClient] = None
        self.write_api: Any = None
        self.query_api: Any = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to InfluxDB and initialize APIs."""
        try:
            self.client = InfluxClient(
                url=self.settings.url, token=self.settings.token, org=self.settings.org
            )

            # Test connection
            ready = self.client.ready()
            if not ready:
                logger.error("InfluxDB is not ready")
                return False

            # Initialize APIs
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()

            self._connected = True
            logger.info(f"Successfully connected to InfluxDB at {self.settings.url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """Check if client is connected to InfluxDB."""
        return self._connected and self.client is not None

    def disconnect(self) -> None:
        """Close the InfluxDB connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("InfluxDB connection closed")

    def write_sensor_reading(self, reading: SensorReading) -> bool:
        """Write a single sensor reading to InfluxDB."""
        if not self.is_connected():
            logger.error("Not connected to InfluxDB")
            return False

        try:
            point_data = reading.to_influx_point()
            point = Point(point_data["measurement"])

            # Add tags
            for tag_key, tag_value in point_data["tags"].items():
                point = point.tag(tag_key, tag_value)

            # Add fields
            for field_key, field_value in point_data["fields"].items():
                point = point.field(field_key, field_value)

            # Set timestamp
            point = point.time(point_data["time"])

            self.write_api.write(bucket=self.settings.bucket, record=point)

            logger.debug(
                f"Written sensor reading: {reading.sensor_id} = {reading.value}"
            )
            return True

        except InfluxDBError as e:
            logger.error(f"InfluxDB error writing sensor reading: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing sensor reading: {e}")
            return False

    def write_system_metric(self, metric: SystemMetric) -> bool:
        """Write a single system metric to InfluxDB."""
        if not self.is_connected():
            logger.error("Not connected to InfluxDB")
            return False

        try:
            point_data = metric.to_influx_point()
            point = Point(point_data["measurement"])

            # Add tags
            for tag_key, tag_value in point_data["tags"].items():
                point = point.tag(tag_key, tag_value)

            # Add fields
            for field_key, field_value in point_data["fields"].items():
                point = point.field(field_key, field_value)

            # Set timestamp
            point = point.time(point_data["time"])

            self.write_api.write(bucket=self.settings.bucket, record=point)

            logger.debug(
                f"Written system metric: {metric.component}.{metric.metric_name} = "
                f"{metric.metric_value}"
            )
            return True

        except InfluxDBError as e:
            logger.error(f"InfluxDB error writing system metric: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing system metric: {e}")
            return False

    def write_batch(
        self,
        data_points: List[Union[SensorReading, SystemMetric, PumpReading, AlarmEvent]],
    ) -> bool:
        """Write multiple data points in a batch."""
        if not self.is_connected():
            logger.error("Not connected to InfluxDB")
            return False

        if not data_points:
            logger.warning("No data points to write")
            return True

        try:
            points = []

            for data_point in data_points:
                point_data = data_point.to_influx_point()
                point = Point(point_data["measurement"])

                # Add tags
                for tag_key, tag_value in point_data["tags"].items():
                    point = point.tag(tag_key, tag_value)

                # Add fields
                for field_key, field_value in point_data["fields"].items():
                    point = point.field(field_key, field_value)

                # Set timestamp
                point = point.time(point_data["time"])
                points.append(point)

            self.write_api.write(bucket=self.settings.bucket, record=points)

            logger.info(f"Written batch of {len(points)} data points")
            return True

        except InfluxDBError as e:
            logger.error(f"InfluxDB error writing batch: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing batch: {e}")
            return False

    def query_data(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Execute a Flux query and return results."""
        if not self.is_connected():
            logger.error("Not connected to InfluxDB")
            return None

        try:
            result = self.query_api.query(query)

            # Convert result to list of dictionaries
            data = []
            for table in result:
                for record in table.records:
                    data.append(record.values)

            return data

        except InfluxDBError as e:
            logger.error(f"InfluxDB error executing query: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return None

    def get_latest_readings(
        self, sensor_id: str, limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get the latest readings for a specific sensor."""
        query = f"""
        from(bucket: "{self.settings.bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "sensors")
          |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: {limit})
        """

        return self.query_data(query)

    def wait_for_connection(
        self, max_retries: int = 30, retry_interval: float = 2.0
    ) -> bool:
        """Wait for InfluxDB to be ready with retries."""
        logger.info("Waiting for InfluxDB to be ready...")

        for attempt in range(max_retries):
            if self.connect():
                return True

            logger.info(
                f"Attempt {attempt + 1}/{max_retries} failed, retrying in "
                f"{retry_interval} seconds..."
            )
            time.sleep(retry_interval)

        logger.error("InfluxDB failed to become ready after maximum retries")
        return False

    def __enter__(self) -> "InfluxDBClient":
        """Context manager entry."""
        if not self.connect():
            raise ConnectionError("Failed to connect to InfluxDB")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
