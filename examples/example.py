#!/usr/bin/env python

"""Example script that reads SHT31 data once per second."""

import sys
import time  # noqa: E402

from sht31.instance import SHT31

sys.path.append(sys.path[0] + "/..")

try:
    import smbus
except ImportError:
    import simulation.smbus as smbus

address = 0x44  # default address
bus = smbus.SMBus(1)

try:
    sensor = SHT31(address=address, bus=bus)
except ValueError as e:
    print("Initializing SHT31 failed:", e)
    sys.exit(1)

while True:
    temperature, humidity = sensor.get_temp_and_humidity()

    if temperature is not None and humidity is not None:
        print(f"Temperature: {temperature:.2f}°C")
        print(f"Relative humidity: {humidity:.2f}%")
    else:
        print("Failed to read SHT31! Check if sensor is connected.")

    time.sleep(1)
