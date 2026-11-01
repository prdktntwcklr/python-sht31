from pathlib import Path

from sht31.exceptions import SHT31ReadError


class SHT31:
    """Read an SHT31 sensor exposed through Linux's hwmon interface."""

    def __init__(self, hwmon_root: str | Path = Path("/sys/class/hwmon")) -> None:
        self._device_path = self._find_device(Path(hwmon_root))

    @staticmethod
    def _find_device(hwmon_root: Path) -> Path:
        if not hwmon_root.is_dir():
            raise SHT31ReadError(f"hwmon directory does not exist: {hwmon_root}")

        try:
            hwmon_devices = sorted(
                path for path in hwmon_root.iterdir() if path.name.startswith("hwmon")
            )
        except OSError as error:
            raise SHT31ReadError(
                f"Failed to list hwmon devices in {hwmon_root}"
            ) from error

        matching_devices: list[Path] = []
        for device_path in hwmon_devices:
            name_path = device_path / "name"
            if not name_path.is_file():
                continue

            try:
                name = name_path.read_text(encoding="utf-8").strip()
            except OSError as error:
                raise SHT31ReadError(f"Failed to read {name_path}") from error

            if name == "sht3x":
                matching_devices.append(device_path)

        if not matching_devices:
            raise SHT31ReadError(f"No sht3x device found in {hwmon_root}")
        if len(matching_devices) > 1:
            raise SHT31ReadError(f"Found multiple sht3x devices in {hwmon_root}")

        return matching_devices[0]

    def _read_attribute(self, attribute: str) -> float:
        attribute_path = self._device_path / attribute
        try:
            value = int(attribute_path.read_text(encoding="utf-8").strip())
        except OSError as error:
            raise SHT31ReadError(f"Failed to read {attribute_path}") from error
        except ValueError as error:
            raise SHT31ReadError(
                f"Invalid integer value in {attribute_path}"
            ) from error

        return value / 1000

    def get_temp_and_humidity(self) -> tuple[float, float]:
        """Return temperature in Celsius and relative humidity in percent."""
        temperature = self._read_attribute("temp1_input")
        humidity = self._read_attribute("humidity1_input")
        return temperature, humidity
