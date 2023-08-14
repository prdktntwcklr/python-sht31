import smbus
import time

# use default I2C address (p9)
I2C_ADDR = 0x44

# get I2C bus
bus = smbus.SMBus(1)

# start high repeatability measurement with clock stretching enabled
bus.write_i2c_block_data(I2C_ADDR, 0x2C, [0x06])

# wait for some time
time.sleep(0.5)

# read data back from 0x00, 6 bytes
# Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
data = bus.read_i2c_block_data(I2C_ADDR, 0x00, 6)

# extract measurement data
temp = data[0] * 256 + data[1]
humidity = data[3] * 256 + data[4]

# convert raw values into physical scale (p14)
celTemp = -45 + (175 * temp / 65535.0)
relHumidity = 100 * humidity / 65535.0

# output values to screen
print("Temperature in Celsius is: {:.2f}".format(celTemp))
print("Relative Humidity is: {:.2f}".format(relHumidity))
