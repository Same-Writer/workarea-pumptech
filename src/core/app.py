"""
Main application class for the PumpTech system.
"""

import logging
import signal
import sys
from typing import Any, Optional

from ..config import get_settings
from ..data_collection import DataCollector
from ..database import InfluxDBClient
from ..hardware import MockHardware
from .logging_setup import setup_logging

logger = logging.getLogger(__name__)


class PumpTechApp:
    """Main application class for the PumpTech system."""

    def __init__(self) -> None:
        """Initialize the PumpTech application."""
        self.settings = get_settings()
        self.data_collector: Optional[DataCollector] = None
        self.running = False

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()

    def initialize(self) -> bool:
        """Initialize the application components."""
        logger.info("Initializing PumpTech application")

        try:
            # Initialize hardware interface
            if self.settings.mock_hardware:
                hardware = MockHardware(self.settings.hardware.__dict__)
                logger.info("Using mock hardware for testing")
            else:
                # In a real implementation, initialize actual hardware here
                logger.warning(
                    "Real hardware not implemented, falling back to mock hardware"
                )
                hardware = MockHardware(self.settings.hardware.__dict__)

            # Initialize database client
            db_client = InfluxDBClient(self.settings)

            # Initialize data collector
            self.data_collector = DataCollector(hardware, db_client)

            logger.info("Application initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False

    def start(self) -> bool:
        """Start the application."""
        if not self.initialize():
            return False

        if not self.settings.data_collection_enabled:
            logger.warning("Data collection is disabled in settings")
            return False

        logger.info("Starting PumpTech application")

        try:
            if self.data_collector is not None and not self.data_collector.start():
                logger.error("Failed to start data collector")
                return False

            self.running = True
            logger.info("PumpTech application started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            return False

    def run(self, collection_interval: float = 1.0) -> None:
        """Run the application with continuous data collection."""
        if not self.start():
            logger.error("Failed to start application")
            sys.exit(1)

        try:
            logger.info(
                f"Running continuous data collection (interval: {collection_interval}s)"
            )
            logger.info("Press Ctrl+C to stop")

            # Run the data collector
            if self.data_collector is not None:
                self.data_collector.run_continuous(collection_interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}")
        finally:
            self.shutdown()

    def run_single_collection(self) -> bool:
        """Run a single data collection cycle."""
        if not self.start():
            return False

        try:
            logger.info("Running single data collection cycle")
            success = (
                self.data_collector.collect_and_store_all()
                if self.data_collector is not None
                else False
            )

            if success:
                logger.info("Single collection cycle completed successfully")
            else:
                logger.error("Single collection cycle failed")

            return success

        except Exception as e:
            logger.error(f"Error during single collection: {e}")
            return False
        finally:
            self.shutdown()

    def get_status(self) -> dict[str, Any]:
        """Get application status."""
        status = {
            "running": self.running,
            "settings": {
                "mock_hardware": self.settings.mock_hardware,
                "data_collection_enabled": self.settings.data_collection_enabled,
                "debug_mode": self.settings.debug_mode,
            },
        }

        if self.data_collector:
            status["data_collector"] = self.data_collector.get_status()

        return status

    def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if not self.running:
            return

        logger.info("Shutting down PumpTech application")
        self.running = False

        if self.data_collector:
            self.data_collector.stop()

        logger.info("Application shutdown complete")

    def __enter__(self) -> "PumpTechApp":
        """Context manager entry."""
        if not self.start():
            raise RuntimeError("Failed to start PumpTech application")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.shutdown()


def main() -> None:
    """Main entry point for the application."""
    # Set up logging first
    setup_logging()

    logger.info("Starting PumpTech Data Collection System")

    # Create and run the application
    app = PumpTechApp()

    # Get collection interval from settings
    settings = get_settings()
    interval = min(
        settings.hardware.temperature_interval,
        settings.hardware.pressure_interval,
        settings.hardware.flow_interval,
    )

    app.run(collection_interval=interval)


if __name__ == "__main__":
    main()
