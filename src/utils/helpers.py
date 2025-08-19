"""
Utility helper functions for the PumpTech system.
"""

from datetime import datetime
from typing import Any, Optional

from ..database.models import SensorReading


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format a timestamp for display."""
    if timestamp is None:
        timestamp = datetime.utcnow()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def validate_sensor_reading(reading: SensorReading) -> bool:
    """Validate a sensor reading for basic correctness."""
    if not reading.sensor_id:
        return False

    if not reading.sensor_type:
        return False

    if reading.value is None:
        return False

    if reading.quality not in ["good", "bad", "uncertain"]:
        return False

    return True


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float with a default fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_moving_average(values: list, window_size: int = 5) -> float:
    """Calculate a simple moving average."""
    if not values or window_size <= 0:
        return 0.0

    # Take the last 'window_size' values
    recent_values = values[-window_size:]
    return float(sum(recent_values) / len(recent_values))


def is_value_in_range(value: float, min_val: float, max_val: float) -> bool:
    """Check if a value is within the specified range."""
    return min_val <= value <= max_val


def generate_alarm_code(source: str, severity: str) -> str:
    """Generate a unique alarm code."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{source.upper()}_{severity.upper()}_{timestamp}"
