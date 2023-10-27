#!/usr/bin/env python

# basic script to test SHT31 functionality on the Raspberry Pi

import smbus
import sys

from sht31 import sht31

address = 0x44
bus = smbus.SMBus(1)

try:
    device = sht31.SHT31(address=address, bus=bus)
except Exception as e:
    print("Initializing SHT31 failed:", e)
    sys.exit(1)

tempCel, humiRel = device.get_temp_and_humidity()

print("Temperature in Celsius is: {:.2f}".format(tempCel))
print("Relative Humidity is: {:.2f}".format(humiRel))
