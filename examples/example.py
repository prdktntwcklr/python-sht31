#!/usr/bin/env python

"""Read SHT31 temperature and humidity once per second via Linux hwmon."""

import sys
import time

from sht31.exceptions import SHT31ReadError
from sht31.instance import SHT31


def main() -> None:
    try:
        sensor = SHT31()
    except SHT31ReadError as error:
        print(f"Initializing SHT31 failed: {error}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            temperature, humidity = sensor.get_temp_and_humidity()
        except SHT31ReadError as error:
            print(f"Failed to read SHT31: {error}", file=sys.stderr)
        else:
            print(f"Temperature: {temperature:.2f}°C")
            print(f"Relative humidity: {humidity:.2f}%")

        time.sleep(1)


if __name__ == "__main__":
    main()
