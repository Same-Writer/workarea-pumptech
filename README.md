# Workarea PumpTech - InfluxDB Data Pipeline

A Python project that demonstrates real-time data collection, storage, and visualization using InfluxDB and Grafana. This project simulates IoT sensor data and system metrics, providing a foundation for time-series data analysis and monitoring dashboards.

## 📋 Overview

This project sets up a complete data pipeline:
1. **Data Generation**: Python script generates simulated sensor data
2. **Data Storage**: InfluxDB stores time-series data
3. **Data Visualization**: Grafana provides real-time dashboards
4. **Containerization**: Docker Compose orchestrates the entire stack

## 🏗️ Project Structure

```
.
├── docker-compose.yml          # Docker services configuration
├── influx-writer.py           # Data generator script
├── .env                       # Environment variables (credentials, ports)
├── influxdb/                  # InfluxDB persistent data
│   └── config/
│       └── influx-configs     # InfluxDB configuration files
├── main.py                    # Main application entry point
├── pyproject.toml            # Python project configuration (UV)
├── README.md                 # This file
├── requirements.txt          # Python dependencies (pip)
├── tests/                    # Test files
│   └── test_main.py         # Unit tests
└── uv.lock                   # UV dependency lock file
```

## 📁 File Descriptions

### Core Application Files
- **`main.py`** - Main application entry point and core business logic
- **`influx-writer.py`** - Standalone script that generates dummy sensor data and writes it to InfluxDB every second
- **`pyproject.toml`** - Modern Python project configuration using UV package manager
- **`requirements.txt`** - Traditional pip requirements file for compatibility
- **`uv.lock`** - Locked dependencies for reproducible builds with UV

### Infrastructure Files
- **`docker-compose.yml`** - Defines InfluxDB and Grafana services with environment variable support
- **`.env`** - Environment configuration file (contains credentials and settings)
- **`influxdb/config/`** - Persistent storage for InfluxDB configuration and data

### Testing Files
- **`tests/test_main.py`** - Unit tests for the main application

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ with UV package manager (recommended) or pip
- `.env` file configured (copy from `.env.example`)

### 1. Setup Environment Configuration

First, create your environment configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred settings
# Default values should work for local development
```

### 2. Install Dependencies

**Using UV (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure Services

```bash
# Start InfluxDB and Grafana
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Start Data Generation

```bash
# Run the data generator
python influx-writer.py

# Or with UV
uv run influx-writer.py
```

You should see log output confirming data is being written every second.

## 🔧 Service Access

Services are accessible using the ports defined in your `.env` file:

### InfluxDB
- **URL**: http://localhost:8087 (or `${INFLUXDB_PORT}` from .env)
- **Username**: `admin` (configurable via `INFLUXDB_ADMIN_USER`)
- **Password**: `adminpassword123` (configurable via `INFLUXDB_ADMIN_PASSWORD`)
- **Organization**: `myorg` (configurable via `INFLUXDB_ORG`)
- **Bucket**: `mybucket` (configurable via `INFLUXDB_BUCKET`)
- **API Token**: `my-super-secret-admin-token` (configurable via `INFLUXDB_ADMIN_TOKEN`)

### Grafana
- **URL**: http://localhost:3000 (or `${GRAFANA_PORT}` from .env)
- **Username**: `admin`
- **Password**: `grafanapassword123` (configurable via `GRAFANA_ADMIN_PASSWORD`)

## ⚙️ Configuration

All service configuration is managed through the `.env` file:

```bash
# InfluxDB Configuration
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=adminpassword123
INFLUXDB_ORG=myorg
INFLUXDB_BUCKET=mybucket
INFLUXDB_ADMIN_TOKEN=my-super-secret-admin-token
INFLUXDB_PORT=8087

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=grafanapassword123
GRAFANA_PORT=3000

# Python Script Configuration
INFLUX_URL=http://localhost:8087
INFLUX_TOKEN=my-super-secret-admin-token
INFLUX_ORG=myorg
INFLUX_BUCKET=mybucket
```

### Environment-Specific Configuration

For different environments, create separate env files:

```bash
# Development
cp .env .env.dev

# Production (with secure passwords)
cp .env .env.prod
# Edit .env.prod with production credentials

# Use specific environment
cp .env.prod .env
docker-compose up -d
```

## 📊 Data Structure

The `influx-writer.py` script generates two types of measurements:

### `sensors` Measurement
- **Tags**: `location`, `sensor_id`
- **Fields**:
  - `value` (integer): Random value 1-100
  - `temperature` (float): Simulated temperature 18-25°C
  - `humidity` (float): Simulated humidity 40-70%

### `system_metrics` Measurement
- **Tags**: `host`
- **Fields**:
  - `cpu_usage` (float): Simulated CPU usage 10-90%
  - `memory_usage` (float): Simulated memory usage 30-80%
  - `random_int` (integer): Random value 1-100

## 🎨 Setting Up Grafana Dashboards

### 1. Configure Data Source
1. Navigate to http://localhost:3000
2. Go to Configuration → Data Sources → Add data source
3. Select **InfluxDB** and configure:
   - **URL**: `http://influxdb:8086` (internal Docker network)
   - **Organization**: Value from your `.env` file (`INFLUXDB_ORG`)
   - **Token**: Value from your `.env` file (`INFLUXDB_ADMIN_TOKEN`)
   - **Default Bucket**: Value from your `.env` file (`INFLUXDB_BUCKET`)

### 2. Create Dashboard
1. Click **+** → Dashboard → Add visualization
2. Use sample queries:

**Random Values Over Time:**
```flux
from(bucket: "mybucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "sensors")
  |> filter(fn: (r) => r["_field"] == "value")
  |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
```

**Current Temperature:**
```flux
from(bucket: "mybucket")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "sensors")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> last()
```

## 🔍 Development Workflow

### Running Tests
```bash
# Run tests with pytest
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_main.py
```

### Code Quality
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

### Adding New Data Types
1. Modify `influx-writer.py` to generate new measurements
2. Update this README with new data structure
3. Create corresponding Grafana visualizations
4. Add tests for new functionality

## 🔧 Configuration

### Environment Variables
All configuration is managed through the `.env` file:
- **Security credentials** (passwords, tokens)
- **Service ports** (InfluxDB, Grafana)
- **Database settings** (organization, bucket names)
- **Connection URLs** for Python scripts

### Customization Options
Edit `.env` to modify:
- Service ports to avoid conflicts
- Admin passwords for security
- Organization and bucket names
- API tokens for authentication

### Python Script Configuration
The `influx-writer.py` automatically loads settings from `.env`:
- Connection URL and credentials
- Retry logic and timeouts
- Data generation parameters

## 🛠️ Troubleshooting

### Port Conflicts
If you encounter "port already in use" errors:
```bash
# Change ports in .env file
echo "INFLUXDB_PORT=9087" >> .env
echo "GRAFANA_PORT=4000" >> .env

# Restart services
docker-compose down
docker-compose up -d
```

### Container Issues
```bash
# View logs
docker-compose logs influxdb
docker-compose logs grafana

# Restart services
docker-compose restart

# Complete reset
docker-compose down -v
docker-compose up -d
```

### Data Not Appearing
1. Ensure `influx-writer.py` is running and showing success logs
2. Check InfluxDB connection in Grafana data source (verify credentials from `.env`)
3. Verify time range in Grafana (try "Last 5 minutes")
4. Confirm bucket name and token match between `.env` and Grafana configuration

### Environment Configuration Issues
```bash
# Verify .env file exists and has correct format
cat .env

# Check if Docker Compose reads variables correctly
docker-compose config

# Test environment variable loading
python -c "import os; print(os.getenv('INFLUX_URL', 'NOT_SET'))"
```

### Python Dependencies
```bash
# Refresh dependencies
uv sync --reinstall

# Or with pip
pip install -r requirements.txt --force-reinstall
```

## 🔐 Security Considerations

### Environment File Security
- **Never commit `.env`** to version control
- Add `.env` to your `.gitignore` file
- Create `.env.example` with placeholder values for team sharing
- Use strong passwords and tokens in production

### Production Deployment
```bash
# Generate secure tokens
INFLUXDB_ADMIN_TOKEN=$(openssl rand -base64 32)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Set restrictive permissions
chmod 600 .env
```

### Team Collaboration
```bash
# Create example file for new developers
cp .env .env.example
# Replace real credentials with placeholders in .env.example
# Share .env.example (safe), never share .env (contains secrets)
```

This project includes:
- **Pre-commit hooks** for code quality
- **GitHub Actions** for automated testing
- **Branch protection** rules for main branch

### Running Locally
```bash
# Install development tools
uv add --dev pre-commit pytest pytest-cov black isort flake8 mypy

# Setup pre-commit
pre-commit install
```

## 🚦 CI/CD

### Grafana Alerts
Set up alerts for:
- High temperature thresholds (>25°C)
- System resource usage (>80%)
- Data ingestion rate drops

### InfluxDB Monitoring
Monitor:
- Database size growth
- Query performance
- Connection counts

## 📈 Monitoring and Alerting

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes and add tests**
4. **Run quality checks**: `pre-commit run --all-files`
5. **Submit a pull request**

### Code Standards
- Follow PEP 8 Python style guide
- Add type hints to all functions
- Include docstrings for public methods
- Maintain test coverage >80%

## 📚 Additional Resources

- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Flux Query Language Guide](https://docs.influxdata.com/influxdb/v2.0/query-data/get-started/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

---

**Need Help?**
- Check the troubleshooting section above
- Review Docker Compose logs: `docker-compose logs`
- Ensure all services are running: `docker-compose ps`
