# SHT31 Temperature & Humidity Sensor

The SHT31 is part of a family of highly accurate temperature and humidity
sensors developed by Sensirion ([www.sensirion.com](https://www.sensirion.com/)).

## Pre-requisites

You need to enable the I2C bus on the Raspberry Pi by running:

```bash
sudo raspi-config nonint do_i2c 0
```

Alternatively, you can run `sudo raspi-config` and enable the I2C bus from the
configuration UI.
