"""Defines constants for the sht31 module."""

from typing import Final

SHT31_ADDRESS_DEF: Final[int] = 0x44  # default address
SHT31_ADDRESS_ALT: Final[int] = 0x45  # alternate address
SHT31_ADDRESSES: Final[list[int]] = [SHT31_ADDRESS_DEF, SHT31_ADDRESS_ALT]

SHT31_RESPONSE_LENGTH: Final[int] = 6

SHT31_MIN_TEMPERATURE: Final[float] = -45.0
SHT31_MAX_TEMPERATURE: Final[float] = 130.0
SHT31_TEMPERATURE_RANGE: Final[float] = SHT31_MAX_TEMPERATURE - SHT31_MIN_TEMPERATURE

SHT31_CMD_SOFTRESET: Final[list[int]] = [0x30, 0xA2]
SHT31_CMD_BREAK: Final[list[int]] = [0x30, 0x93]
SHT31_CMD_HEATER_ON: Final[list[int]] = [0x30, 0x6D]
SHT31_CMD_HEATER_OFF: Final[list[int]] = [0x30, 0x66]
SHT31_CMD_READSTATUS: Final[list[int]] = [0xF3, 0x2D]
SHT31_CMD_CLEARSTATUS: Final[list[int]] = [0x30, 0x41]

# group related commands together
# Attribution: adafruit/Adafruit_CircuitPython_SHT31D
SHT31_REP_HIGH: Final[str] = "High"
SHT31_REP_MED: Final[str] = "Medium"
SHT31_REP_LOW: Final[str] = "Low"

SHT31_SINGLE_COMMANDS: Final[list[tuple[str, bool, list[int]]]] = [
    (SHT31_REP_HIGH, True, [0x2C, 0x06]),
    (SHT31_REP_MED, True, [0x2C, 0x0D]),
    (SHT31_REP_LOW, True, [0x2C, 0x10]),
    (SHT31_REP_HIGH, False, [0x24, 0x00]),
    (SHT31_REP_MED, False, [0x24, 0x0B]),
    (SHT31_REP_LOW, False, [0x24, 0x16]),
]
