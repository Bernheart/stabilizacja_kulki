import os
import yaml
from dataclasses import dataclass

@dataclass
class SerialConfig:
    port: str
    baudrate: int
    timeout: int


@dataclass
class WatchdogConfig:
    enabled: bool
    interval_seconds: int


class AppConfig:
    def __init__(self, path: str = None):
        # Use the directory of this script as base
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = path or os.path.join(base_dir, "config.yaml")
        
        self.serial: SerialConfig | None = None
        self.watchdog: WatchdogConfig | None = None
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.serial = SerialConfig(
            port=data["serial"]["port"],
            baudrate=data["serial"]["baudrate"],
            timeout=data["serial"]['timeout']
        )
        self.watchdog = WatchdogConfig(
            enabled=data["watchdog"]["enabled"],
            interval_seconds=data["watchdog"]["interval_seconds"]
        )

    def save(self):
        """Save configuration to YAML file."""
        data = {
            "serial": {
                "port": self.serial.port,
                "baudrate": self.serial.baudrate,
                "time": self.serial.timeout
            },
            "watchdog": {
                "enabled": self.watchdog.enabled,
                "interval_seconds": self.watchdog.interval_seconds
            }
        }
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)

    def __repr__(self):
        return (
            f"AppConfig(serial={self.serial}, "
            f"watchdog={self.watchdog})"
        )