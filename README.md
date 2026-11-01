# SHT31 Temperature & Humidity Sensor

This Linux-focused Python package reads temperature and relative humidity from
an SHT31 sensor through the Linux kernel's `sht3x` hwmon driver. The kernel
driver handles sensor communication; this package reads the values exposed by
the driver.

The SHT31 is part of a family of highly accurate temperature and humidity
sensors developed by [Sensirion AG](https://www.sensirion.com/).

## Prerequisites

- Linux with the I2C bus enabled and the sensor connected.
- The kernel `sht3x` driver enabled and bound to the sensor.
- Python 3.11 or newer.

On Raspberry Pi OS, enable I2C with:

```bash
sudo raspi-config nonint do_i2c 0
```

Alternatively, run `sudo raspi-config` and enable I2C in the configuration UI.
The sensor must also be instantiated on the I2C bus so the kernel driver can
bind to it. See the Linux kernel documentation for
[instantiating I2C devices](https://docs.kernel.org/i2c/instantiating-devices.html)
and the [`sht3x` hwmon driver](https://docs.kernel.org/hwmon/sht3x.html).

Check that the driver has exposed the sensor:

```bash
grep -H . /sys/class/hwmon/hwmon*/name
```

One of the results should be `sht3x`. The library discovers the device by this
name; it does not depend on a particular `hwmon` number. It currently expects
exactly one `sht3x` device.

## Installing the library

Download the latest release from the
[Releases](https://github.com/prdktntwcklr/python-sht31/releases) page and
install its source distribution with `pip`:

```bash
python -m pip install python-sht31-0.1.1.tar.gz
```

When a GitHub release is published, the release workflow checks that its tag
matches the version in `pyproject.toml` (for example, tag `v0.1.1` for version
`0.1.1`). If they differ, the workflow fails without building or attaching
artifacts. When they match, it builds the package and attaches the wheel and
source distribution to the release. Draft releases are not built until
published.

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then
sync the locked development dependencies and run the test suite:

```bash
uv sync
uv run pytest tests -vv
```

Build the source distribution and wheel with:

```bash
uv build
```

## Usage

```python
from sht31.exceptions import SHT31ReadError
from sht31.instance import SHT31

try:
    sensor = SHT31()
    temperature, humidity = sensor.get_temp_and_humidity()
except SHT31ReadError as error:
    print(f"Could not read the SHT31: {error}")
else:
    print(f"Temperature: {temperature:.2f}°C")
    print(f"Relative humidity: {humidity:.2f}%")
```

Temperature is returned in degrees Celsius and relative humidity in percent.
The kernel exports both values in thousandths, which the library converts
before returning them. Device discovery and attribute read failures raise
`SHT31ReadError`.

The package reads the kernel interface only. It does not expose low-level
sensor commands such as reset or repeatability configuration.

An example that continuously prints readings is available in
[`examples/example.py`](./examples/example.py).
