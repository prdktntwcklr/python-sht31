from sht31 import sht31

import pytest


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    mocker.patch("time.sleep")
    yield


@pytest.fixture(scope='function')
def device(mocker):
    smbus = mocker.Mock()
    device = sht31.SHT31(bus=smbus)
    yield device


def test_default_address(device):
    """
    Tests that the I2C address defaults to 0x44
    """
    assert device._address == 0x44


def test_no_bus_error():
    """
    Tests that a RuntimeError is raised when the no I2C is specified
    """
    with pytest.raises(ValueError) as excinfo:
        NoBusDevice = sht31.SHT31()
    assert str(excinfo.value) == "I2C bus not specified!"


def test_wrong_address_error(mocker):
    """
    Tests that a RuntimeError is raised when an invalid I2C address is provided
    """
    smbus = mocker.Mock()
    with pytest.raises(ValueError) as excinfo:
        BadAddrDevice = sht31.SHT31(address=0xAB, bus=smbus)
    assert str(excinfo.value) == "Invalid I2C address: 0xab!"


def test_humidity_conversion(device):
    """
    Tests the conversion to relative humidity
    """
    assert device._calc_relative_humidity(0) == 0.0
    assert device._calc_relative_humidity(65535) == 100.0


def test_celsius_conversion(device):
    """
    Tests the conversion to Celsius temperature
    """
    assert device._calc_celsius_temperature(0) == -45.0
    assert device._calc_celsius_temperature(65535) == 130.0


def test_read_data(device, mocker):
    """
    Tests the read data function
    """
    mocker.patch.object(device._bus, 'read_i2c_block_data', return_value=[0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC])

    temp, humi = device._read_data()

    assert temp == 0x1234
    assert humi == 0x789A


def test_read_and_convert_data_fail(device, mocker):
    """
    Tests the read and convert data function when read_i2c_block_data fails
    """
    mocker.patch.object(device._bus, 'read_i2c_block_data', side_effect=Exception)
    temp, humi = device._read_and_convert_data()

    assert temp is None
    assert humi is None


def test_read_data_fail(device, mocker):
    """
    Tests the read data function with read_i2c_block_data failing
    """
    mocker.patch.object(device._bus, 'read_i2c_block_data', side_effect=Exception)
    temp, humi = device._read_and_convert_data()

    assert temp is None
    assert humi is None


def test_setup_func(device, mocker):
    """
    Tests the setup function
    """
    mocker.patch.object(device._bus, 'write_i2c_block_data')
    device._setup()
    device._bus.write_i2c_block_data.assert_called_once_with(0x44, 0x2C, [0x06])
