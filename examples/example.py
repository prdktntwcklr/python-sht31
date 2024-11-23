#!/usr/bin/env python

''' example script that reads SHT31 data once per second '''

# pylint: disable=broad-exception-caught,consider-using-f-string

import sys
import time  # noqa: E402

from sht31 import sht31  # noqa: E402

sys.path.append(sys.path[0] + "/..")

try:
    import smbus
except ImportError:
    import simulation.smbus as smbus

address = 0x44  # default address
bus = smbus.SMBus(1)

try:
    sht31 = sht31.SHT31(address=address, bus=bus)
except Exception as e:
    print("Initializing SHT31 failed:", e)
    sys.exit(1)

while True:
    temperature, humidity = sht31.get_temp_and_humidity()

    if temperature is not None and humidity is not None:
        print("Temperature: {:.2f}°C".format(temperature))
        print("Relative humidity: {:.2f}%".format(humidity))
    else:
        print("Failed to read SHT31! Check if sensor is connected.")

    time.sleep(1)
