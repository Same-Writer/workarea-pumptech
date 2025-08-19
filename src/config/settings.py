"""
Configuration settings for the PumpTech system.

Handles environment variables and configuration management.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


def load_env_file(filepath: str = ".env") -> None:
    """Load environment variables from .env file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


@dataclass
class InfluxDBSettings:
    """InfluxDB connection settings."""

    url: str = "http://localhost:8087"
    token: str = "my-super-secret-admin-token"
    org: str = "myorg"
    bucket: str = "mybucket"

    @classmethod
    def from_env(cls) -> "InfluxDBSettings":
        """Create settings from environment variables."""
        return cls(
            url=os.getenv("INFLUX_URL", cls.url),
            token=os.getenv("INFLUX_TOKEN", cls.token),
            org=os.getenv("INFLUX_ORG", cls.org),
            bucket=os.getenv("INFLUX_BUCKET", cls.bucket),
        )


@dataclass
class HardwareSettings:
    """Hardware configuration settings."""

    # Serial port settings
    serial_port: str = "/dev/ttyUSB0"
    serial_baudrate: int = 9600
    serial_timeout: float = 1.0

    # I2C settings
    i2c_bus: int = 1

    # GPIO settings
    gpio_pins: Dict[str, int] = field(default_factory=dict)

    # Sensor polling intervals (seconds)
    temperature_interval: float = 1.0
    pressure_interval: float = 1.0
    flow_interval: float = 0.5

    def __post_init__(self) -> None:
        if not self.gpio_pins:
            self.gpio_pins = {
                "pump_control": 18,
                "valve_control": 19,
                "emergency_stop": 20,
                "status_led": 21,
            }

    @classmethod
    def from_env(cls) -> "HardwareSettings":
        """Create settings from environment variables."""
        return cls(
            serial_port=os.getenv("SERIAL_PORT", cls.serial_port),
            serial_baudrate=int(os.getenv("SERIAL_BAUDRATE", str(cls.serial_baudrate))),
            serial_timeout=float(os.getenv("SERIAL_TIMEOUT", str(cls.serial_timeout))),
            i2c_bus=int(os.getenv("I2C_BUS", str(cls.i2c_bus))),
            temperature_interval=float(
                os.getenv("TEMP_INTERVAL", str(cls.temperature_interval))
            ),
            pressure_interval=float(
                os.getenv("PRESSURE_INTERVAL", str(cls.pressure_interval))
            ),
            flow_interval=float(os.getenv("FLOW_INTERVAL", str(cls.flow_interval))),
        )


@dataclass
class LoggingSettings:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    @classmethod
    def from_env(cls) -> "LoggingSettings":
        """Create settings from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", cls.level),
            format=os.getenv("LOG_FORMAT", cls.format),
            file_path=os.getenv("LOG_FILE_PATH"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(cls.max_file_size))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", str(cls.backup_count))),
        )


@dataclass
class Settings:
    """Main application settings."""

    influxdb: InfluxDBSettings
    hardware: HardwareSettings
    logging: LoggingSettings

    # Application settings
    data_collection_enabled: bool = True
    mock_hardware: bool = False
    debug_mode: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        # Load .env file first
        load_env_file()

        return cls(
            influxdb=InfluxDBSettings.from_env(),
            hardware=HardwareSettings.from_env(),
            logging=LoggingSettings.from_env(),
            data_collection_enabled=os.getenv("DATA_COLLECTION_ENABLED", "true").lower()
            == "true",
            mock_hardware=os.getenv("MOCK_HARDWARE", "false").lower() == "true",
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
