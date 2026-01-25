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
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x00, 6)
        except:
            raise SHT31ReadError

        tempRaw = data[0] * 256 + data[1]
        humiRaw = data[3] * 256 + data[4]

        return tempRaw, humiRaw

    def _read_and_convert_data(self) -> tuple[float, float] | tuple[None, None]:
        try:
            tempRaw, humiRaw = self._read_data()
        except SHT31ReadError:
            return None, None

        tempCelsius = self._calc_celsius_temperature(tempRaw)
        humiRelative = self._calc_relative_humidity(humiRaw)

        return tempCelsius, humiRelative

    def _calc_relative_humidity(self, humiVal: int) -> float:
        return 100 * humiVal / (65536.0 - 1.0)

    def _calc_celsius_temperature(self, tempVal: int) -> float:
        return -45 + (175 * tempVal / (65536.0 - 1.0))

    def _command(self, command: int) -> None:
        cmd = struct.pack(">H", command)

        self._bus.write_i2c_block_data(self._address, cmd[0], [cmd[1]])

    def _setup(self) -> None:
        for command in SHT31_SINGLE_COMMANDS:
            if (
                self._repeatability == command[0]
                and self._clock_stretching == command[1]
            ):
                self._command(command[2])
        time.sleep(0.5)

    def reset(self) -> None:
        self._command(SHT31_CMD_BREAK)
        time.sleep(0.001)
        self._command(SHT31_CMD_SOFTRESET)
        time.sleep(0.0015)

    def get_temp_and_humidity(self) -> tuple[float | None, float | None]:
        self._setup()

        tempCelsius, humiRelative = self._read_and_convert_data()

        return tempCelsius, humiRelative
