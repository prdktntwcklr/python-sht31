I2C_ADDRESS = 0x44
I2C_ADDRESS_ALT = 0x45

valid_addresses = [I2C_ADDRESS, I2C_ADDRESS_ALT]

class SHT31():
   def __init__(self, address = I2C_ADDRESS, bus = None):
      if address not in valid_addresses:
         raise RuntimeError(f"Invalid I2C address! Should be one of {list(map(hex, valid_addresses))}!")

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

   def setup(self) -> None:
      # start high repeatability measurement with clock stretching enabled
      self._bus.write_i2c_block_data(self._address, 0x2C, [0x06])

   def get_temp_and_humidity(self) -> tuple[int, int]:
      tempRaw, humiRaw = self._read_data()

      tempCelsius = self._calc_celsius_temperature(tempRaw)
      humiRelative = self._calc_relative_humidity(humiRaw)

      return tempCelsius, humiRelative