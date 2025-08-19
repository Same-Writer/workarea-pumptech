"""
Mock hardware implementation for testing and development.

Simulates hardware sensors and pumps with realistic data patterns.
"""

import math
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..database.models import AlarmEvent, PumpReading, SensorReading
from .base import HardwareInterface, PumpInterface, SensorInterface


class MockSensor(SensorInterface):
    """Mock sensor implementation with realistic data patterns."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        location: str = "unknown",
        base_value: float = 20.0,
        variation: float = 5.0,
        unit: str = "",
    ):
        """Initialize mock sensor with configurable parameters."""
        super().__init__(sensor_id, sensor_type, location)
        self.base_value = base_value
        self.variation = variation
        self.unit = unit
        self.start_time = time.time()
        self.healthy = True

    def read(self) -> Optional[SensorReading]:
        """Generate a realistic sensor reading."""
        if not self.healthy:
            self._set_error("Sensor is not healthy")
            return None

        try:
            # Generate realistic data with some patterns
            elapsed = time.time() - self.start_time

            # Add some sine wave pattern for realistic variation
            sine_component = math.sin(elapsed / 60) * (self.variation * 0.3)

            # Add random noise
            noise = random.uniform(-self.variation * 0.2, self.variation * 0.2)

            # Occasional spikes or dips
            if random.random() < 0.05:  # 5% chance
                spike = random.uniform(-self.variation, self.variation)
            else:
                spike = 0

            value = self.base_value + sine_component + noise + spike

            # Ensure value stays within reasonable bounds
            min_val = self.base_value - self.variation * 2
            max_val = self.base_value + self.variation * 2
            value = max(min_val, min(max_val, value))

            reading = SensorReading(
                location=self.location,
                sensor_id=self.sensor_id,
                sensor_type=self.sensor_type,
                value=round(value, 2),
                unit=self.unit,
                quality="good",
                timestamp=datetime.utcnow(),
                metadata={
                    "mock": True,
                    "base_value": self.base_value,
                    "variation": self.variation,
                },
            )

            self.last_reading = reading
            return reading

        except Exception as e:
            self._set_error(f"Failed to read sensor: {e}")
            return None

    def calibrate(self, **kwargs: Any) -> bool:
        """Mock calibration - always succeeds."""
        return True

    def is_healthy(self) -> bool:
        """Check sensor health."""
        return self.healthy

    def set_health(self, healthy: bool) -> None:
        """Set sensor health status for testing."""
        self.healthy = healthy


class MockPump(PumpInterface):
    """Mock pump implementation with realistic behavior."""

    def __init__(self, pump_id: str, location: str = "unknown"):
        """Initialize mock pump."""
        super().__init__(pump_id, location)
        self.target_speed = 0.0
        self.actual_speed = 0.0
        self.start_time = time.time()
        self.total_runtime = 0.0
        self.healthy = True

    def start(self) -> bool:
        """Start the pump."""
        if not self.healthy:
            self._set_error("Pump is not healthy")
            return False

        self.is_running = True
        if self.target_speed == 0:
            self.target_speed = 50.0  # Default to 50% speed
        return True

    def stop(self) -> bool:
        """Stop the pump."""
        self.is_running = False
        self.target_speed = 0.0
        return True

    def set_speed(self, speed_percent: float) -> bool:
        """Set pump speed."""
        if not 0 <= speed_percent <= 100:
            self._set_error("Speed must be between 0 and 100 percent")
            return False

        self.target_speed = speed_percent
        if speed_percent > 0:
            self.is_running = True
        else:
            self.is_running = False

        return True

    def get_status(self) -> Dict[str, Any]:
        """Get pump status."""
        # Simulate gradual speed changes
        if self.is_running:
            speed_diff = self.target_speed - self.actual_speed
            if abs(speed_diff) > 1:
                self.actual_speed += speed_diff * 0.1  # Gradual change
            else:
                self.actual_speed = self.target_speed

        return {
            "pump_id": self.pump_id,
            "is_running": self.is_running,
            "target_speed": self.target_speed,
            "actual_speed": round(self.actual_speed, 1),
            "healthy": self.healthy,
            "total_runtime": self.total_runtime,
        }

    def get_readings(self) -> Optional[PumpReading]:
        """Get comprehensive pump readings."""
        if not self.healthy:
            return None

        # status = self.get_status()  # TODO: Use this for more realistic simulation
        # elapsed = time.time() - self.start_time  # TODO: Use for wear simulation

        # Generate realistic pump data based on speed
        speed_factor = self.actual_speed / 100.0

        # Flow rate (L/min) - proportional to speed with some variation
        base_flow = 100.0  # Max flow at 100% speed
        flow_rate = base_flow * speed_factor + random.uniform(-2, 2)
        flow_rate = max(0, int(round(flow_rate)))  # Convert to integer

        # Pressure (bar) - increases with speed
        base_pressure = 5.0
        pressure = base_pressure * speed_factor + random.uniform(-0.2, 0.2)
        pressure = max(0, int(round(pressure)))  # Convert to integer

        # Temperature (°C) - increases with load
        ambient_temp = 25.0
        temp_rise = speed_factor * 15.0  # Up to 15°C rise at full speed
        temperature = ambient_temp + temp_rise + random.uniform(-1, 1)

        # Power consumption (W) - quadratic relationship with speed
        base_power = 1000.0  # Max power at 100% speed
        power = base_power * (speed_factor**2) + random.uniform(-20, 20)
        power = max(0, int(round(power)))  # Convert to integer

        # RPM - proportional to speed
        max_rpm = 3000.0
        rpm = max_rpm * speed_factor + random.uniform(-50, 50)
        rpm = max(0.0, float(round(rpm, 0)))  # Ensure it's always a float with .0

        # Vibration - increases with speed and wear
        base_vibration = 0.1
        vibration = base_vibration + speed_factor * 0.5 + random.uniform(-0.05, 0.05)
        vibration = max(0, vibration)

        return PumpReading(
            location=self.location,
            sensor_id=self.pump_id,
            sensor_type="pump",
            value=flow_rate,  # Already an integer
            unit="L/min",
            quality="good",
            timestamp=datetime.utcnow(),
            flow_rate=flow_rate,  # Already an integer
            pressure=pressure,  # Already an integer
            temperature=round(temperature, 2),
            power_consumption=power,  # Already an integer
            rpm=rpm,  # Already a float
            vibration=round(vibration, 3),
            metadata={
                "mock": True,
                "target_speed": self.target_speed,
                "actual_speed": self.actual_speed,
                "is_running": self.is_running,
            },
        )

    def emergency_stop(self) -> bool:
        """Emergency stop the pump."""
        self.is_running = False
        self.target_speed = 0.0
        self.actual_speed = 0.0
        return True

    def set_health(self, healthy: bool) -> None:
        """Set pump health status for testing."""
        self.healthy = healthy


class MockHardware(HardwareInterface):
    """Mock hardware system with multiple sensors and pumps."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize mock hardware system."""
        super().__init__(config)
        self.sensors: Dict[str, MockSensor] = {}
        self.pumps: Dict[str, MockPump] = {}
        self.alarms: List[AlarmEvent] = []
        self._setup_default_hardware()

    def _setup_default_hardware(self) -> None:
        """Set up default sensors and pumps."""
        # Temperature sensors
        self.sensors["temp_001"] = MockSensor(
            "temp_001", "temperature", "inlet", 22.0, 3.0, "°C"
        )
        self.sensors["temp_002"] = MockSensor(
            "temp_002", "temperature", "outlet", 25.0, 2.0, "°C"
        )

        # Pressure sensors
        self.sensors["press_001"] = MockSensor(
            "press_001", "pressure", "inlet", 2.5, 0.5, "bar"
        )
        self.sensors["press_002"] = MockSensor(
            "press_002", "pressure", "outlet", 4.0, 0.8, "bar"
        )

        # Flow sensors
        self.sensors["flow_001"] = MockSensor(
            "flow_001", "flow", "main_line", 75.0, 10.0, "L/min"
        )

        # Level sensors
        self.sensors["level_001"] = MockSensor(
            "level_001", "level", "tank_1", 60.0, 15.0, "%"
        )

        # Pumps
        self.pumps["pump_001"] = MockPump("pump_001", "main_station")
        self.pumps["pump_002"] = MockPump("pump_002", "backup_station")

    def connect(self) -> bool:
        """Connect to mock hardware."""
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from mock hardware."""
        self.connected = False

    def is_connected(self) -> bool:
        """Check connection status."""
        return self.connected

    def read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """Read a specific sensor."""
        if not self.connected:
            self._set_error("Hardware not connected")
            return None

        sensor = self.sensors.get(sensor_id)
        if not sensor:
            self._set_error(f"Sensor {sensor_id} not found")
            return None

        return sensor.read()

    def read_all_sensors(self) -> List[SensorReading]:
        """Read all sensors."""
        readings = []
        for sensor in self.sensors.values():
            reading = sensor.read()
            if reading:
                readings.append(reading)
        return readings

    def get_pump_data(self, pump_id: str) -> Optional[PumpReading]:
        """Get pump data."""
        if not self.connected:
            self._set_error("Hardware not connected")
            return None

        pump = self.pumps.get(pump_id)
        if not pump:
            self._set_error(f"Pump {pump_id} not found")
            return None

        return pump.get_readings()

    def control_pump(self, pump_id: str, action: str, **kwargs: Any) -> bool:
        """Control pump operations."""
        if not self.connected:
            self._set_error("Hardware not connected")
            return False

        pump = self.pumps.get(pump_id)
        if not pump:
            self._set_error(f"Pump {pump_id} not found")
            return False

        if action == "start":
            return pump.start()
        elif action == "stop":
            return pump.stop()
        elif action == "set_speed":
            speed = kwargs.get("speed", 0)
            return pump.set_speed(speed)
        elif action == "emergency_stop":
            return pump.emergency_stop()
        else:
            self._set_error(f"Unknown pump action: {action}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        sensor_count = len(self.sensors)
        healthy_sensors = sum(1 for s in self.sensors.values() if s.is_healthy())

        pump_count = len(self.pumps)
        running_pumps = sum(1 for p in self.pumps.values() if p.is_running)

        return {
            "connected": self.connected,
            "sensors": {
                "total": sensor_count,
                "healthy": healthy_sensors,
                "unhealthy": sensor_count - healthy_sensors,
            },
            "pumps": {
                "total": pump_count,
                "running": running_pumps,
                "stopped": pump_count - running_pumps,
            },
            "alarms": {
                "total": len(self.alarms),
                "unacknowledged": sum(1 for a in self.alarms if not a.acknowledged),
            },
            "mock_hardware": True,
        }

    def get_alarms(self) -> List[AlarmEvent]:
        """Get current alarms."""
        # Occasionally generate random alarms for testing
        if random.random() < 0.01:  # 1% chance per call
            alarm = AlarmEvent(
                source="mock_system",
                severity=random.choice(["info", "warning", "error"]),
                category="system",
                message=f"Mock alarm generated at {datetime.utcnow()}",
                alarm_code=f"MOCK_{random.randint(1000, 9999)}",
                acknowledged=False,
            )
            self.alarms.append(alarm)

        return self.alarms.copy()

    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """Acknowledge an alarm."""
        for alarm in self.alarms:
            if alarm.alarm_code == alarm_id:
                alarm.acknowledged = True
                return True
        return False

    def add_sensor(self, sensor: MockSensor) -> None:
        """Add a sensor to the mock hardware."""
        self.sensors[sensor.sensor_id] = sensor

    def add_pump(self, pump: MockPump) -> None:
        """Add a pump to the mock hardware."""
        self.pumps[pump.pump_id] = pump

    def simulate_sensor_failure(self, sensor_id: str) -> None:
        """Simulate a sensor failure for testing."""
        if sensor_id in self.sensors:
            self.sensors[sensor_id].set_health(False)

    def simulate_pump_failure(self, pump_id: str) -> None:
        """Simulate a pump failure for testing."""
        if pump_id in self.pumps:
            self.pumps[pump_id].set_health(False)
