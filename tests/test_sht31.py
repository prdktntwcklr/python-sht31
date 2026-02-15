# pylint: disable=protected-access,redefined-outer-name

from sht31 import instance, constants
from sht31.exceptions import SHT31ReadError

import pytest

from pytest_mock import MockerFixture
from typing import Generator


@pytest.fixture(autouse=True)
def patch_sleep(mocker: MockerFixture) -> Generator[None, None, None]:
    mocker.patch("time.sleep")
    yield


@pytest.fixture(scope="function")
def device(mocker: MockerFixture) -> Generator["instance.SHT31", None, None]:
    smbus = mocker.Mock()
    device = instance.SHT31(bus=smbus)
    yield device


def test_default_address(device: instance.SHT31) -> None:
    """
    Tests that the I2C device address defaults to 0x44.
    """
    assert device._address == 0x44


def test_overriding_address(mocker: MockerFixture) -> None:
    """
    Tests that the I2C device address can be overriden to 0x45.
    """
    smbus = mocker.Mock()
    alt_addr_device = instance.SHT31(address=0x45, bus=smbus)
    assert alt_addr_device._address == 0x45


def test_no_bus_error() -> None:
    """
    Tests that a RuntimeError is raised when the no I2C is specified.
    """
    with pytest.raises(ValueError) as excinfo:
        no_bus_device = instance.SHT31()
    assert str(excinfo.value) == "I2C bus not specified!"


def test_wrong_address_error(mocker: MockerFixture) -> None:
    """
    Tests that a RuntimeError is raised when an invalid I2C address is provided.
    """
    smbus = mocker.Mock()
    with pytest.raises(ValueError) as excinfo:
        bad_addr_device = instance.SHT31(address=0xAB, bus=smbus)
    assert str(excinfo.value) == "Invalid I2C address: 0xab!"


def test_humidity_conversion(device: instance.SHT31) -> None:
    """
    Tests the conversion to relative humidity.
    """
    assert device._calc_relative_humidity(0) == 0.0
    assert device._calc_relative_humidity(0x1234) == pytest.approx(7.11, 0.1)
    assert device._calc_relative_humidity(0xFFFF) == 100.0

    # test values out of range
    assert device._calc_relative_humidity(-100) == 0.0
    assert device._calc_relative_humidity(0x12345) == 100.0


def test_celsius_conversion(device: instance.SHT31) -> None:
    """
    Tests the conversion to Celsius temperature.
    """
    assert device._calc_celsius_temperature(0) == -45.0
    assert device._calc_celsius_temperature(0x1234) == pytest.approx(-32.55, 0.1)
    assert device._calc_celsius_temperature(0xFFFF) == 130.0

    # test values out of range
    assert device._calc_celsius_temperature(-100) == -45.0
    assert device._calc_celsius_temperature(0x12345) == 130.0


def test_read_data(device: instance.SHT31, mocker: MockerFixture) -> None:
    """
    Tests the read data function.
    """
    mocker.patch.object(
        device._bus,
        "read_i2c_block_data",
        return_value=[0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC],
    )

    temp, humi = device._read_data()

    assert temp == 0x1234
    assert humi == 0x789A


def test_fail_read_data(device: instance.SHT31, mocker: MockerFixture) -> None:
    """
    Tests the read data function when read_i2c_block_data only returns 5 bytes.
    """
    mocker.patch.object(
        device._bus,
        "read_i2c_block_data",
        return_value=[0x12, 0x34, 0x56, 0x78, 0x9A],
    )

    with pytest.raises(SHT31ReadError):
        _, _ = device._read_data()


def test_read_and_convert_data_fail(
    device: instance.SHT31, mocker: MockerFixture
) -> None:
    """
    Tests the read and convert data function when read_i2c_block_data fails.
    """
    mocker.patch.object(device._bus, "read_i2c_block_data", side_effect=OSError)
    temp, humi = device._read_and_convert_data()

    assert temp is None
    assert humi is None


def test_read_data_fail(device: instance.SHT31, mocker: MockerFixture) -> None:
    """
    Tests the read data function with read_i2c_block_data failing.
    """
    mocker.patch.object(device._bus, "read_i2c_block_data", side_effect=OSError)
    temp, humi = device._read_and_convert_data()

    assert temp is None
    assert humi is None


def test_send_measurement_cmd_function(
    device: instance.SHT31, mocker: MockerFixture
) -> None:
    """
    Tests the _send_measurement_cmd function.
    """
    mocker.patch.object(device._bus, "write_i2c_block_data")
    device._send_measurement_cmd()
    device._bus.write_i2c_block_data.assert_called_once_with(0x44, 0x24, [0x00])


def test_command_function(device: instance.SHT31, mocker: MockerFixture) -> None:
    """
    Tests the command function.
    """
    mocker.patch.object(device._bus, "write_i2c_block_data")
    device._command(constants.SHT31_CMD_SOFTRESET)
    device._bus.write_i2c_block_data.assert_called_once_with(0x44, 0x30, [0xA2])
