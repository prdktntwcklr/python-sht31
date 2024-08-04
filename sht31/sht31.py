import struct
import time

from sht31.exceptions import SHT31ReadError

_SHT31_ADDRESS_DEF = 0x44
_SHT31_ADDRESS_ALT = 0x45
_SHT31_ADDRESSES = [_SHT31_ADDRESS_DEF, _SHT31_ADDRESS_ALT]

_SHT31_CMD_SOFTRESET = 0x30A2
_SHT31_CMD_BREAK = 0x3093
_SHT31_CMD_HEATER_ON = 0x306D
_SHT31_CMD_HEATER_OFF = 0x3066
_SHT31_CMD_READSTATUS = 0xF32D
_SHT31_CMD_CLEARSTATUS = 0x3041

# group related commands together
# Attribution: adafruit/Adafruit_CircuitPython_SHT31D
REP_HIGH = "High"
REP_MED = "Medium"
REP_LOW = "Low"

_SHT31_SINGLE_COMMANDS = (
    (REP_HIGH, True, 0x2C06),
    (REP_MED, True, 0x2C0D),
    (REP_LOW, True, 0x2C10),
    (REP_HIGH, False, 0x2400),
    (REP_MED, False, 0x240B),
    (REP_LOW, False, 0x2416)
)


class SHT31:
    def __init__(self, address=_SHT31_ADDRESS_DEF, bus=None):
        if address not in _SHT31_ADDRESSES:
            raise ValueError(f"Invalid I2C address: {hex(address)}!")

        if not bus:
            raise ValueError("I2C bus not specified!")

        self._address = address
        self._bus = bus

        # use high repeatability single-shot measurement with clock stretching
        # TODO: let user change these settings
        self._repeatability = REP_HIGH
        self._clock_stretching = True

    def _read_data(self) -> tuple[int, int]:
        try:
            data = self._bus.read_i2c_block_data(self._address, 0x00, 6)
        except:
            raise SHT31ReadError

        tempRaw = data[0] * 256 + data[1]
        humiRaw = data[3] * 256 + data[4]

        return tempRaw, humiRaw

    def _read_and_convert_data(self) -> tuple[float, float]:
        try:
            tempRaw, humiRaw = self._read_data()
        except SHT31ReadError:
            return None, None

        tempCelsius = self._calc_celsius_temperature(tempRaw)
        humiRelative = self._calc_relative_humidity(humiRaw)

        return tempCelsius, humiRelative

    def _calc_relative_humidity(self, humiVal: int) -> float:
        return (100 * humiVal / (65536.0 - 1.0))

    def _calc_celsius_temperature(self, tempVal: int) -> float:
        return (-45 + (175 * tempVal / (65536.0 - 1.0)))

    def _command(self, command: int) -> None:
        cmd = struct.pack('>H', command)

        self._bus.write_i2c_block_data(self._address, cmd[0], [cmd[1]])

    def _setup(self) -> None:
        for command in _SHT31_SINGLE_COMMANDS:
            if (
                self._repeatability == command[0] and
                self._clock_stretching == command[1]
            ):
                self._command(command[2])
        time.sleep(0.5)

    def reset(self) -> None:
        self._command(_SHT31_CMD_BREAK)
        time.sleep(0.001)
        self._command(_SHT31_CMD_SOFTRESET)
        time.sleep(0.0015)

    def get_temp_and_humidity(self) -> tuple[float, float]:
        self._setup()

        tempCelsius, humiRelative = self._read_and_convert_data()

        return tempCelsius, humiRelative
