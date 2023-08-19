import struct
import time

_SHT31_ADDRESS_DEF = 0x44
_SHT31_ADDRESS_ALT = 0x45
_SHT31_ADDRESSES = [_SHT31_ADDRESS_DEF, _SHT31_ADDRESS_ALT]

_SHT31_CMD_SOFTRESET = 0x30A2
_SHT31_CMD_SETUP = 0x2C06
_SHT31_CMD_BREAK = 0x3093
_SHT31_CMD_HEATER_ON = 0x306D
_SHT31_CMD_HEATER_OFF = 0x3066
_SHT31_CMD_READSTATUS = 0xF32D
_SHT31_CMD_CLEARSTATUS = 0x3041

class SHT31:
   def __init__(self, address = _SHT31_ADDRESS_DEF, bus = None):
      if address not in _SHT31_ADDRESSES:
         raise RuntimeError(f"Invalid I2C address: {hex(address)}!")

      if not bus:
         raise RuntimeError("I2C bus not specified!")

      self._address = address
      self._bus = bus

   def _read_data(self) -> tuple[int, int]:
      data = self._bus.read_i2c_block_data(self._address, 0x00, 6)

      tempRaw = data[0] * 256 + data[1]
      humiRaw = data[3] * 256 + data[4]

      return tempRaw, humiRaw

   def _calc_relative_humidity(self, humiVal: int) -> float:
      return (100 * humiVal / (65536.0 - 1.0))

   def _calc_celsius_temperature(self, tempVal: int) -> float:
      return (-45 + (175 * tempVal / (65536.0 - 1.0)))
   
   def _command(self, command: int) -> None:
      cmd = struct.pack('>H', command)

      self._bus.write_i2c_block_data(self._address, cmd[0], [cmd[1]])

   def setup(self) -> None:
      self._command(_SHT31_CMD_SETUP)
      time.sleep(10)

   def reset(self) -> None:
      self._command(_SHT31_CMD_BREAK)
      time.sleep(0.001)
      self._command(_SHT31_CMD_SOFTRESET)
      time.sleep(0.0015)

   def get_temp_and_humidity(self) -> tuple[int, int]:
      tempRaw, humiRaw = self._read_data()

      tempCelsius = self._calc_celsius_temperature(tempRaw)
      humiRelative = self._calc_relative_humidity(humiRaw)

      return tempCelsius, humiRelative