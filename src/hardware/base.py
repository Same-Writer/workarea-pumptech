"""
Base hardware interface for the PumpTech system.

Defines the abstract interface that all hardware implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..database.models import AlarmEvent, PumpReading, SensorReading


class HardwareInterface(ABC):
    """Abstract base class for hardware interfaces."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the hardware interface with configuration."""
        self.config = config
        self.connected = False
        self.last_error: Optional[str] = None

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the hardware. Returns True if successful."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the hardware."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if hardware is connected."""
        pass

    @abstractmethod
    def read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """Read a single sensor value."""
        pass

    @abstractmethod
    def read_all_sensors(self) -> List[SensorReading]:
        """Read all available sensors."""
        pass

    @abstractmethod
    def get_pump_data(self, pump_id: str) -> Optional[PumpReading]:
        """Get comprehensive pump data."""
        pass

    @abstractmethod
    def control_pump(self, pump_id: str, action: str, **kwargs: Any) -> bool:
        """Control pump operations (start, stop, set_speed, etc.)."""
        pass

    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        pass

    @abstractmethod
    def get_alarms(self) -> List[AlarmEvent]:
        """Get current alarms/alerts."""
        pass

    @abstractmethod
    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """Acknowledge an alarm."""
        pass

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self.last_error

    def _set_error(self, error_message: str) -> None:
        """Set the last error message."""
        self.last_error = error_message

    def __enter__(self) -> "HardwareInterface":
        """Context manager entry."""
        if not self.connect():
            raise ConnectionError(f"Failed to connect to hardware: {self.last_error}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()


class SensorInterface(ABC):
    """Abstract base class for individual sensor interfaces."""

    def __init__(self, sensor_id: str, sensor_type: str, location: str = "unknown"):
        """Initialize the sensor interface."""
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.last_reading: Optional[SensorReading] = None
        self.last_error: Optional[str] = None

    @abstractmethod
    def read(self) -> Optional[SensorReading]:
        """Read the sensor value and return a SensorReading object."""
        pass

    @abstractmethod
    def calibrate(self, **kwargs: Any) -> bool:
        """Calibrate the sensor."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the sensor is functioning properly."""
        pass

    def get_last_reading(self) -> Optional[SensorReading]:
        """Get the last successful reading."""
        return self.last_reading

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self.last_error

    def _set_error(self, error_message: str) -> None:
        """Set the last error message."""
        self.last_error = error_message


class PumpInterface(ABC):
    """Abstract base class for pump interfaces."""

    def __init__(self, pump_id: str, location: str = "unknown"):
        """Initialize the pump interface."""
        self.pump_id = pump_id
        self.location = location
        self.is_running = False
        self.current_speed = 0.0
        self.last_error: Optional[str] = None

    @abstractmethod
    def start(self) -> bool:
        """Start the pump."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stop the pump."""
        pass

    @abstractmethod
    def set_speed(self, speed_percent: float) -> bool:
        """Set pump speed as percentage (0-100)."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current pump status."""
        pass

    @abstractmethod
    def get_readings(self) -> Optional[PumpReading]:
        """Get comprehensive pump readings."""
        pass

    @abstractmethod
    def emergency_stop(self) -> bool:
        """Emergency stop the pump."""
        pass

    def get_last_error(self) -> Optional[str]:
        """Get the last error message."""
        return self.last_error

    def _set_error(self, error_message: str) -> None:
        """Set the last error message."""
        self.last_error = error_message
