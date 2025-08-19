# PumpTech Data Collection and Monitoring System

A modular Python system for collecting data from hardware sensors and pumps, storing it in InfluxDB, and providing real-time monitoring capabilities. The system features a clean architecture with hardware abstraction, mock implementations for testing, and comprehensive data collection services.

## 📋 Overview

This project provides a complete IoT data pipeline with:
1. **Hardware Abstraction**: Modular interfaces for sensors and pumps with mock implementations
2. **Data Collection**: Automated collection from multiple hardware sources
3. **Data Storage**: InfluxDB integration with structured data models
4. **Configuration Management**: Environment-based settings with validation
5. **Monitoring**: Real-time dashboards with Grafana
6. **Testing**: Mock hardware for development and testing

## 🏗️ Project Structure

```
workarea-pumptech/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Environment-based settings
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── app.py                # Main application class
│   │   └── logging_setup.py      # Logging configuration
│   ├── database/                 # Database interfaces
│   │   ├── __init__.py
│   │   ├── influx_client.py      # Enhanced InfluxDB client
│   │   └── models.py             # Data models (SensorReading, PumpReading, etc.)
│   ├── hardware/                 # Hardware abstraction layer
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract interfaces
│   │   └── mock_hardware.py      # Mock implementation for testing
│   ├── data_collection/          # Data collection services
│   │   ├── __init__.py
│   │   └── collector.py          # Main data collection logic
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── scripts/                      # Utility scripts
│   └── legacy_influx_writer.py   # Original influx writer (moved)
├── docs/                         # Documentation
├── examples/                     # Example configurations
├── tests/                        # Test files
│   └── test_main.py
├── influxdb/                     # InfluxDB persistent data
│   └── config/
├── main.py                       # Application entry point
├── docker-compose.yml            # Docker services configuration
├── pyproject.toml               # Python project configuration
├── .env.example                 # Environment configuration template
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ with UV package manager (recommended) or pip
- Docker and Docker Compose for InfluxDB/Grafana
- Git for version control

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Same-Writer/workarea-pumptech.git
cd workarea-pumptech

# Create environment configuration
cp .env.example .env
# Edit .env with your preferred settings (defaults work for development)
```

### 2. Install Dependencies

**Using UV (recommended):**
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

**Using pip:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Start Infrastructure Services

```bash
# Start InfluxDB and Grafana
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Run the Application

```bash
# Run with UV
uv run python main.py

# Or with activated virtual environment
python main.py
```

You should see log output showing:
- Application initialization
- Hardware connection (mock mode by default)
- InfluxDB connection
- Data collection cycles

## ⚙️ Configuration

### Environment Variables

The system uses environment-based configuration through the `.env` file:

```bash
# InfluxDB Configuration
INFLUX_URL=http://localhost:8087
INFLUX_TOKEN=my-super-secret-admin-token
INFLUX_ORG=myorg
INFLUX_BUCKET=mybucket

# Hardware Configuration
SERIAL_PORT=/dev/ttyUSB0
SERIAL_BAUDRATE=9600
I2C_BUS=1

# Sensor Polling Intervals (seconds)
TEMP_INTERVAL=1.0
PRESSURE_INTERVAL=1.0
FLOW_INTERVAL=0.5

# Application Settings
DATA_COLLECTION_ENABLED=true
MOCK_HARDWARE=true          # Set to false for real hardware
DEBUG_MODE=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/pumptech.log
```

### Hardware Dependencies

For real hardware integration, uncomment dependencies in `pyproject.toml`:

```toml
dependencies = [
    "influxdb-client>=1.49.0",
    "pyserial>=3.5",           # For serial communication
    "RPi.GPIO>=0.7.1",         # For Raspberry Pi GPIO
    "smbus2>=0.4.0",           # For I2C communication
    "modbus-tk>=1.1.2",        # For Modbus communication
    "paho-mqtt>=1.6.0",        # For MQTT communication
    # ... more hardware dependencies
]
```

Then reinstall:
```bash
uv sync  # or pip install -e .
```

## 🔧 Service Access

### InfluxDB
- **URL**: http://localhost:8087
- **Username**: `admin`
- **Password**: `adminpassword123`
- **Organization**: `myorg`
- **Bucket**: `mybucket`
- **Token**: `my-super-secret-admin-token`

### Grafana
- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `grafanapassword123`

## 📊 Data Models

The system defines structured data models for different types of readings:

### SensorReading
```python
@dataclass
class SensorReading:
    measurement: str = "sensors"
    location: str = "unknown"
    sensor_id: str = "unknown"
    sensor_type: str = "unknown"
    value: float = 0.0
    unit: str = ""
    quality: str = "good"  # good, bad, uncertain
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
```

### PumpReading
```python
@dataclass
class PumpReading(SensorReading):
    measurement: str = "pump_data"
    sensor_type: str = "pump"
    flow_rate: float = 0.0
    pressure: float = 0.0
    temperature: float = 0.0
    power_consumption: float = 0.0
    rpm: float = 0.0
    vibration: float = 0.0
```

### SystemMetric
```python
@dataclass
class SystemMetric:
    measurement: str = "system_metrics"
    host: str = "unknown"
    component: str = "unknown"
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
```

## 🔌 Hardware Integration

### Mock Hardware (Default)

The system includes comprehensive mock hardware that simulates:
- **Temperature sensors** with realistic variations
- **Pressure sensors** with configurable ranges
- **Flow sensors** with dynamic readings
- **Pump controllers** with speed control and monitoring
- **System alarms** and health monitoring

### Real Hardware Implementation

To add real hardware:

1. **Create hardware implementation**:
```python
# src/hardware/my_hardware.py
from .base import HardwareInterface

class MyHardware(HardwareInterface):
    def connect(self) -> bool:
        # Implement actual hardware connection
        pass

    def read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        # Implement sensor reading
        pass
```

2. **Update configuration**:
```bash
# .env
MOCK_HARDWARE=false
```

3. **Modify main application**:
```python
# src/core/app.py
from ..hardware.my_hardware import MyHardware

# Replace MockHardware with MyHardware
```

## 🧪 Development and Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_main.py
```

### Code Quality

```bash
# Install development dependencies
uv sync --group dev

# Format code
uv run black src/
uv run isort src/

# Lint code
uv run flake8 src/
uv run mypy src/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Mock Hardware Testing

The mock hardware provides realistic simulation for development:

```python
# Test individual sensors
from src.hardware.mock_hardware import MockHardware

hardware = MockHardware({})
hardware.connect()

# Read all sensors
readings = hardware.read_all_sensors()
print(f"Collected {len(readings)} sensor readings")

# Test pump control
pump_reading = hardware.get_pump_data("pump_001")
hardware.control_pump("pump_001", "start")
hardware.control_pump("pump_001", "set_speed", speed=75)
```

## 📈 Grafana Dashboard Setup

### 1. Configure InfluxDB Data Source

1. Navigate to http://localhost:3000
2. Go to **Configuration** → **Data Sources** → **Add data source**
3. Select **InfluxDB** and configure:
   - **Query Language**: Flux
   - **URL**: `http://influxdb:8086` (internal Docker network)
   - **Organization**: `myorg` (from your `.env`)
   - **Token**: `my-super-secret-admin-token` (from your `.env`)
   - **Default Bucket**: `mybucket` (from your `.env`)

### 2. Sample Queries

**Temperature Over Time:**
```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensors")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["sensor_type"] == "temperature")
  |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)
```

**Pump Performance:**
```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "pump_data")
  |> filter(fn: (r) => r["_field"] == "flow_rate" or r["_field"] == "pressure")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

**System Health:**
```flux
from(bucket: "mybucket")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "system_metrics")
  |> filter(fn: (r) => r["metric_name"] == "sensors_healthy")
  |> last()
```

## 🔧 Advanced Configuration

### Custom Hardware Implementation

Create your own hardware interface:

```python
# src/hardware/custom_hardware.py
from typing import List, Optional
from .base import HardwareInterface, SensorInterface, PumpInterface
from ..database.models import SensorReading, PumpReading

class CustomSensor(SensorInterface):
    def __init__(self, sensor_id: str, port: str):
        super().__init__(sensor_id, "custom", "field")
        self.port = port

    def read(self) -> Optional[SensorReading]:
        # Implement your sensor reading logic
        # e.g., read from serial port, I2C, etc.
        pass

    def calibrate(self, **kwargs) -> bool:
        # Implement calibration logic
        return True

    def is_healthy(self) -> bool:
        # Implement health check
        return True

class CustomHardware(HardwareInterface):
    def __init__(self, config):
        super().__init__(config)
        self.sensors = {}
        self.pumps = {}

    def connect(self) -> bool:
        # Initialize hardware connections
        try:
            # Add your sensors
            self.sensors["temp_001"] = CustomSensor("temp_001", "/dev/ttyUSB0")
            # Add your pumps
            # self.pumps["pump_001"] = CustomPump("pump_001", "192.168.1.100")
            return True
        except Exception as e:
            self._set_error(str(e))
            return False
```

### Environment-Specific Configurations

Create different configuration files for different environments:

```bash
# Development
cp .env.example .env.dev
# Edit .env.dev with development settings

# Production
cp .env.example .env.prod
# Edit .env.prod with production settings

# Testing
cp .env.example .env.test
# Edit .env.test with test database settings
```

### Logging Configuration

Customize logging in your `.env`:

```bash
# Enable file logging
LOG_FILE_PATH=logs/pumptech.log

# Set log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=DEBUG

# Configure log rotation
LOG_MAX_FILE_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

## 🛠️ Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the project directory
cd workarea-pumptech

# Reinstall dependencies
uv sync --reinstall
```

**2. InfluxDB Connection Issues**
```bash
# Check if InfluxDB is running
docker-compose ps

# View InfluxDB logs
docker-compose logs influxdb

# Test connection manually
curl http://localhost:8087/health
```

**3. Port Conflicts**
```bash
# Change ports in .env
INFLUXDB_PORT=9087
GRAFANA_PORT=4000

# Restart services
docker-compose down && docker-compose up -d
```

**4. Data Not Appearing**
- Verify `.env` configuration matches Docker services
- Check application logs for errors
- Ensure `DATA_COLLECTION_ENABLED=true`
- Verify time range in Grafana (try "Last 5 minutes")

### Debug Mode

Enable debug mode for detailed logging:

```bash
# .env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### Performance Tuning

For high-frequency data collection:

```bash
# .env - Adjust polling intervals
TEMP_INTERVAL=0.1    # 100ms
PRESSURE_INTERVAL=0.1
FLOW_INTERVAL=0.05   # 50ms
```

## 🔐 Security Considerations

### Production Deployment

1. **Change default passwords**:
```bash
# Generate secure credentials
INFLUX_TOKEN=$(openssl rand -base64 32)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
```

2. **Secure file permissions**:
```bash
chmod 600 .env
```

3. **Use environment-specific configurations**:
```bash
# Never commit .env to version control
echo ".env" >> .gitignore
```

### Network Security

- Use HTTPS in production
- Configure firewall rules
- Use VPN for remote access
- Enable InfluxDB authentication

## 📚 API Reference

### DataCollector Methods

```python
from src.data_collection import DataCollector

collector = DataCollector()

# Start collection
collector.start()

# Single collection cycle
success = collector.collect_and_store_all()

# Get status
status = collector.get_status()

# Stop collection
collector.stop()
```

### Hardware Interface Methods

```python
from src.hardware import MockHardware

hardware = MockHardware({})
hardware.connect()

# Read sensors
readings = hardware.read_all_sensors()
single_reading = hardware.read_sensor("temp_001")

# Control pumps
hardware.control_pump("pump_001", "start")
hardware.control_pump("pump_001", "set_speed", speed=50)
pump_data = hardware.get_pump_data("pump_001")

# System status
status = hardware.get_system_status()
alarms = hardware.get_alarms()
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes and add tests**
4. **Run quality checks**: `uv run pre-commit run --all-files`
5. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests before committing
uv run pytest --cov=src
```

### Code Standards

- Follow PEP 8 Python style guide
- Add type hints to all functions
- Include docstrings for public methods
- Maintain test coverage >80%
- Use meaningful variable and function names

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

## 📚 Additional Resources

- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Flux Query Language Guide](https://docs.influxdata.com/influxdb/v2.0/query-data/get-started/)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**Need Help?**
- Check the troubleshooting section above
- Review application logs: `uv run python main.py`
- Check Docker services: `docker-compose logs`
- Open an issue on GitHub for bugs or feature requests
