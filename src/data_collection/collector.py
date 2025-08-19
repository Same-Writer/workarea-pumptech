"""
Data collection service for the PumpTech system.

Handles collecting data from hardware and storing it in InfluxDB.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..config import get_settings
from ..database import InfluxDBClient
from ..database.models import AlarmEvent, PumpReading, SensorReading, SystemMetric
from ..hardware import HardwareInterface, MockHardware

logger = logging.getLogger(__name__)


class DataCollector:
    """Main data collection service."""

    def __init__(
        self,
        hardware: Optional[HardwareInterface] = None,
        db_client: Optional[InfluxDBClient] = None,
    ):
        """Initialize the data collector."""
        self.settings = get_settings()

        # Initialize hardware interface
        if hardware is None:
            if self.settings.mock_hardware:
                hardware = MockHardware(self.settings.hardware.__dict__)
            else:
                # In a real implementation, you would initialize actual hardware here
                logger.warning("Real hardware not implemented, using mock hardware")
                hardware = MockHardware(self.settings.hardware.__dict__)

        self.hardware = hardware

        # Initialize database client
        if db_client is None:
            db_client = InfluxDBClient()

        self.db_client = db_client

        # Collection state
        self.running = False
        self.last_collection_time: Optional[datetime] = None
        self.collection_count = 0
        self.error_count = 0

    def start(self) -> bool:
        """Start the data collection service."""
        logger.info("Starting data collection service")

        # Connect to hardware
        if not self.hardware.connect():
            logger.error(
                f"Failed to connect to hardware: {self.hardware.get_last_error()}"
            )
            return False

        # Connect to database
        if not self.db_client.wait_for_connection():
            logger.error("Failed to connect to InfluxDB")
            return False

        self.running = True
        logger.info("Data collection service started successfully")
        return True

    def stop(self) -> None:
        """Stop the data collection service."""
        logger.info("Stopping data collection service")
        self.running = False

        if self.hardware:
            self.hardware.disconnect()

        if self.db_client:
            self.db_client.disconnect()

        logger.info("Data collection service stopped")

    def collect_sensor_data(self) -> List[SensorReading]:
        """Collect data from all sensors."""
        if not self.hardware.is_connected():
            logger.error("Hardware not connected")
            return []

        try:
            readings = self.hardware.read_all_sensors()
            logger.debug(f"Collected {len(readings)} sensor readings")
            return readings

        except Exception as e:
            logger.error(f"Error collecting sensor data: {e}")
            self.error_count += 1
            return []

    def collect_pump_data(self) -> List[PumpReading]:
        """Collect data from all pumps."""
        if not self.hardware.is_connected():
            logger.error("Hardware not connected")
            return []

        pump_readings = []

        try:
            # Get system status to find available pumps
            # status = self.hardware.get_system_status()  # TODO: Use for discovery

            # For mock hardware, we know the pump IDs
            # In real implementation, you'd get this from hardware discovery
            pump_ids = ["pump_001", "pump_002"]  # This should come from hardware config

            for pump_id in pump_ids:
                try:
                    reading = self.hardware.get_pump_data(pump_id)
                    if reading:
                        pump_readings.append(reading)
                except Exception as e:
                    logger.warning(f"Failed to read pump {pump_id}: {e}")

            logger.debug(f"Collected {len(pump_readings)} pump readings")
            return pump_readings

        except Exception as e:
            logger.error(f"Error collecting pump data: {e}")
            self.error_count += 1
            return []

    def collect_system_metrics(self) -> List[SystemMetric]:
        """Collect system performance metrics."""
        metrics = []

        try:
            # Get hardware system status
            if self.hardware.is_connected():
                status = self.hardware.get_system_status()

                # Convert status to metrics
                metrics.append(
                    SystemMetric(
                        host="pumptech_system",
                        component="hardware",
                        metric_name="sensors_healthy",
                        metric_value=float(status.get("sensors", {}).get("healthy", 0)),
                        metric_unit="count",
                        additional_fields={
                            "total_sensors": status.get("sensors", {}).get("total", 0),
                            "unhealthy_sensors": status.get("sensors", {}).get(
                                "unhealthy", 0
                            ),
                        },
                    )
                )

                metrics.append(
                    SystemMetric(
                        host="pumptech_system",
                        component="hardware",
                        metric_name="pumps_running",
                        metric_value=float(status.get("pumps", {}).get("running", 0)),
                        metric_unit="count",
                        additional_fields={
                            "total_pumps": status.get("pumps", {}).get("total", 0),
                            "stopped_pumps": status.get("pumps", {}).get("stopped", 0),
                        },
                    )
                )

            # Add collection service metrics
            metrics.append(
                SystemMetric(
                    host="pumptech_system",
                    component="data_collector",
                    metric_name="collection_count",
                    metric_value=float(self.collection_count),
                    metric_unit="count",
                    additional_fields={
                        "error_count": self.error_count,
                        "running": self.running,
                    },
                )
            )

            logger.debug(f"Collected {len(metrics)} system metrics")
            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            self.error_count += 1
            return []

    def collect_alarms(self) -> List[AlarmEvent]:
        """Collect current alarms from hardware."""
        if not self.hardware.is_connected():
            return []

        try:
            alarms = self.hardware.get_alarms()
            logger.debug(f"Collected {len(alarms)} alarms")
            return alarms

        except Exception as e:
            logger.error(f"Error collecting alarms: {e}")
            self.error_count += 1
            return []

    def store_data(self, data_points: List[Any]) -> bool:
        """Store collected data points in InfluxDB."""
        if not data_points:
            return True

        if not self.db_client.is_connected():
            logger.error("Database not connected")
            return False

        try:
            success = self.db_client.write_batch(data_points)
            if success:
                logger.debug(f"Stored {len(data_points)} data points")
            else:
                logger.error("Failed to store data points")
                self.error_count += 1

            return success

        except Exception as e:
            logger.error(f"Error storing data: {e}")
            self.error_count += 1
            return False

    def collect_and_store_all(self) -> bool:
        """Collect all data and store it."""
        if not self.running:
            return False

        start_time = time.time()
        all_data: List[Union[SensorReading, PumpReading, SystemMetric, AlarmEvent]] = []

        try:
            # Collect sensor data
            sensor_readings = self.collect_sensor_data()
            all_data.extend(sensor_readings)

            # Collect pump data
            pump_readings = self.collect_pump_data()
            all_data.extend(pump_readings)

            # Collect system metrics
            system_metrics = self.collect_system_metrics()
            all_data.extend(system_metrics)

            # Collect alarms
            alarms = self.collect_alarms()
            all_data.extend(alarms)

            # Store all data
            success = self.store_data(all_data)

            # Update collection statistics
            self.collection_count += 1
            self.last_collection_time = datetime.utcnow()

            collection_time = time.time() - start_time
            logger.info(
                f"Collection cycle completed: {len(all_data)} data points "
                f"in {collection_time:.2f}s (success: {success})"
            )

            return success

        except Exception as e:
            logger.error(f"Error in collection cycle: {e}")
            self.error_count += 1
            return False

    def run_continuous(self, interval: float = 1.0) -> None:
        """Run continuous data collection."""
        logger.info(f"Starting continuous data collection (interval: {interval}s)")

        if not self.start():
            logger.error("Failed to start data collection service")
            return

        try:
            while self.running:
                self.collect_and_store_all()
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")

        except Exception as e:
            logger.error(f"Unexpected error in continuous collection: {e}")

        finally:
            self.stop()

    def get_status(self) -> Dict[str, Any]:
        """Get collector status information."""
        return {
            "running": self.running,
            "hardware_connected": self.hardware.is_connected()
            if self.hardware
            else False,
            "database_connected": self.db_client.is_connected()
            if self.db_client
            else False,
            "collection_count": self.collection_count,
            "error_count": self.error_count,
            "last_collection_time": self.last_collection_time.isoformat()
            if self.last_collection_time
            else None,
            "settings": {
                "mock_hardware": self.settings.mock_hardware,
                "data_collection_enabled": self.settings.data_collection_enabled,
                "debug_mode": self.settings.debug_mode,
            },
        }

    def __enter__(self) -> "DataCollector":
        """Context manager entry."""
        if not self.start():
            raise RuntimeError("Failed to start data collector")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()
