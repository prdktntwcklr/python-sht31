import smbus
import time
import sht31

address = 0x44
bus = smbus.SMBus(1)

device = sht31.SHT31(address = address, bus = bus)

device.setup()

time.sleep(0.5)

tempCel, humiRel = device.get_temp_and_humidity()

print("Temperature in Celsius is: {:.2f}".format(tempCel))
print("Relative Humidity is: {:.2f}".format(humiRel))
