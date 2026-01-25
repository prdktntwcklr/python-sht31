"""Defines constants for the sht31 module."""

from typing import Final

SHT31_ADDRESS_DEF: Final[int] = 0x44  # default address
SHT31_ADDRESS_ALT: Final[int] = 0x45  # alternate address
SHT31_ADDRESSES: list[int] = [SHT31_ADDRESS_DEF, SHT31_ADDRESS_ALT]

SHT31_CMD_SOFTRESET: Final[int] = 0x30A2
SHT31_CMD_BREAK: Final[int] = 0x3093
SHT31_CMD_HEATER_ON: Final[int] = 0x306D
SHT31_CMD_HEATER_OFF: Final[int] = 0x3066
SHT31_CMD_READSTATUS: Final[int] = 0xF32D
SHT31_CMD_CLEARSTATUS: Final[int] = 0x3041

# group related commands together
# Attribution: adafruit/Adafruit_CircuitPython_SHT31D
SHT31_REP_HIGH: Final[str] = "High"
SHT31_REP_MED: Final[str] = "Medium"
SHT31_REP_LOW: Final[str] = "Low"

SHT31_SINGLE_COMMANDS: Final[list[tuple[str, bool, int]]] = [
    (SHT31_REP_HIGH, True, 0x2C06),
    (SHT31_REP_MED, True, 0x2C0D),
    (SHT31_REP_LOW, True, 0x2C10),
    (SHT31_REP_HIGH, False, 0x2400),
    (SHT31_REP_MED, False, 0x240B),
    (SHT31_REP_LOW, False, 0x2416),
]
