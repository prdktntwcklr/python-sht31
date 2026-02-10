try:
    import smbus
except ImportError:
    import simulation.smbus as smbus

import struct
import time

from sht31.constants import (
    SHT31_ADDRESSES,
    SHT31_REP_HIGH,
    SHT31_SINGLE_COMMANDS,
    SHT31_CMD_BREAK,
    SHT31_CMD_SOFTRESET,
)
from sht31.exceptions import SHT31ReadError


class SHT31:
    def __init__(self, address: int = SHT31_ADDRESSES[0], bus: smbus = None) -> None:
        if address not in SHT31_ADDRESSES:
            raise ValueError(f"Invalid I2C address: {hex(address)}!")

        if not bus:
            raise ValueError("I2C bus not specified!")

        self._address = address
        self._bus = bus

        # use high repeatability single-shot measurement with clock stretching
        # TODO: let user change these settings
        self._repeatability = SHT31_REP_HIGH
        self._clock_stretching = True

    def _read_data(self) -> tuple[int, int]:
        """
        Read raw temperature and humidity data from the sensor.

        Returns:
            tuple[int, int]: (temperature_raw, humidity_raw)

        Raises:
            SHT31ReadError: If reading from the sensor fails.
        """
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x00, 6)
        except OSError as e:
            raise SHT31ReadError("Failed to read data from sensor") from e

        if len(data) != 6:
            raise SHT31ReadError(f"Unexpected data length: {len(data)} bytes")

        temp_raw = (data[0] << 8) | data[1]
        humi_raw = (data[3] << 8) | data[4]

        return temp_raw, humi_raw

    def _read_and_convert_data(self) -> tuple[float, float] | tuple[None, None]:
        try:
            temp_raw, humi_raw = self._read_data()
        except SHT31ReadError:
            return None, None

        temp_celsius = self._calc_celsius_temperature(temp_raw)
        humi_relative = self._calc_relative_humidity(humi_raw)

        return temp_celsius, humi_relative

    def _calc_relative_humidity(self, raw: int) -> float:
        """
        Convert 16-bit raw humidity value to percentage (0.0 to 100.0).
        """
        raw = max(0, min(0xFFFF, raw))
        return (raw / 0xFFFF) * 100.0

    def _calc_celsius_temperature(self, raw: int) -> float:
        """
        Convert 16-bit raw temperature value to degrees Celsius.

        Formula: T = -45 + 175 * raw / (2^16 - 1)
        """
        raw = max(0, min(0xFFFF, raw))
        return -45.0 + (175.0 * raw) / 0xFFFF

    def _command(self, command: int) -> None:
        cmd = struct.pack(">H", command)

        self._bus.write_i2c_block_data(self._address, cmd[0], [cmd[1]])

    def _setup(self) -> None:
        """
        Configure the sensor for measurement if it has not been initialized.
        """
        if getattr(self, "_initialized", False):
            return

        for repeatability, clock_stretching, command in SHT31_SINGLE_COMMANDS:
            if (
                self._repeatability == repeatability
                and self._clock_stretching == clock_stretching
            ):
                self._command(command)
                break

        time.sleep(0.5)
        self._initialized = True

    def reset(self) -> None:
        self._command(SHT31_CMD_BREAK)
        time.sleep(0.001)
        self._command(SHT31_CMD_SOFTRESET)
        time.sleep(0.0015)

    def get_temp_and_humidity(self) -> tuple[float | None, float | None]:
        """
        Read temperature and relative humidity from the sensor.

        Returns:
            A tuple (temperature_celsius, relative_humidity) where each value
            is a float if the measurement succeeds, or None if the value
            could not be obtained.
        """
        self._setup()

        temp_celsius, humi_relative = self._read_and_convert_data()

        return temp_celsius, humi_relative
