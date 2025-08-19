"""
Data models for the PumpTech system.

Defines the structure of data points that will be stored in InfluxDB.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class SensorReading:
    """Represents a sensor reading data point."""

    # Measurement name in InfluxDB
    measurement: str = "sensors"

    # Tags (indexed fields)
    location: str = "unknown"
    sensor_id: str = "unknown"
    sensor_type: str = "unknown"

    # Fields (data values)
    value: float = 0.0
    unit: str = ""
    quality: str = "good"  # good, bad, uncertain

    # Timestamp
    timestamp: Optional[datetime] = None

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        point = {
            "measurement": self.measurement,
            "tags": {
                "location": self.location,
                "sensor_id": self.sensor_id,
                "sensor_type": self.sensor_type,
            },
            "fields": {
                "value": self.value,
                "unit": self.unit,
                "quality": self.quality,
            },
            "time": self.timestamp,
        }

        # Add metadata as additional fields
        if self.metadata is not None:
            point["fields"].update(self.metadata)  # type: ignore[union-attr]

        return point


@dataclass
class SystemMetric:
    """Represents a system metric data point."""

    # Measurement name in InfluxDB
    measurement: str = "system_metrics"

    # Tags (indexed fields)
    host: str = "unknown"
    component: str = "unknown"

    # Fields (data values)
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""

    # Timestamp
    timestamp: Optional[datetime] = None

    # Additional fields
    additional_fields: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.additional_fields is None:
            self.additional_fields = {}

    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        point = {
            "measurement": self.measurement,
            "tags": {
                "host": self.host,
                "component": self.component,
            },
            "fields": {
                "metric_name": self.metric_name,
                "metric_value": self.metric_value,
                "metric_unit": self.metric_unit,
            },
            "time": self.timestamp,
        }

        # Add additional fields
        if self.additional_fields is not None:
            point["fields"].update(self.additional_fields)  # type: ignore[union-attr]

        return point


@dataclass
class PumpReading(SensorReading):
    """Specialized sensor reading for pump data."""

    measurement: str = "pump_data"
    sensor_type: str = "pump"

    # Pump-specific fields
    flow_rate: float = 0.0
    pressure: float = 0.0
    temperature: float = 0.0
    power_consumption: float = 0.0
    rpm: float = 0.0
    vibration: float = 0.0

    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format with pump-specific fields."""
        point = super().to_influx_point()

        # Add pump-specific fields
        pump_fields = {
            "flow_rate": self.flow_rate,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "power_consumption": self.power_consumption,
            "rpm": self.rpm,
            "vibration": self.vibration,
        }

        point["fields"].update(pump_fields)
        return point


@dataclass
class AlarmEvent:
    """Represents an alarm or event data point."""

    # Measurement name in InfluxDB
    measurement: str = "alarms"

    # Tags (indexed fields)
    source: str = "unknown"
    severity: str = "info"  # info, warning, error, critical
    category: str = "system"

    # Fields (data values)
    message: str = ""
    alarm_code: str = ""
    acknowledged: bool = False

    # Timestamp
    timestamp: Optional[datetime] = None

    # Additional context
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.context is None:
            self.context = {}

    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        point = {
            "measurement": self.measurement,
            "tags": {
                "source": self.source,
                "severity": self.severity,
                "category": self.category,
            },
            "fields": {
                "message": self.message,
                "alarm_code": self.alarm_code,
                "acknowledged": self.acknowledged,
            },
            "time": self.timestamp,
        }

        # Add context as additional fields
        if self.context is not None:
            point["fields"].update(self.context)  # type: ignore[union-attr]

        return point
