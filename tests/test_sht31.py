from pathlib import Path

import pytest

from sht31.exceptions import SHT31ReadError
from sht31.instance import SHT31


def create_hwmon_device(
    hwmon_root: Path,
    directory: str = "hwmon0",
    name: str = "sht3x",
    temperature: str = "21500",
    humidity: str = "48300",
) -> Path:
    device_path = hwmon_root / directory
    device_path.mkdir(parents=True)
    (device_path / "name").write_text(name, encoding="utf-8")
    (device_path / "temp1_input").write_text(temperature, encoding="utf-8")
    (device_path / "humidity1_input").write_text(humidity, encoding="utf-8")
    return device_path


def test_reads_and_converts_hwmon_values(tmp_path: Path) -> None:
    hwmon_root = tmp_path / "hwmon"
    create_hwmon_device(
        hwmon_root,
        directory="hwmon7",
        temperature="21500\n",
        humidity="48300\n",
    )
    (hwmon_root / "hwmon0").mkdir()

    sensor = SHT31(hwmon_root=hwmon_root)

    assert sensor.get_temp_and_humidity() == pytest.approx((21.5, 48.3))


def test_discovers_sht3x_among_other_hwmon_devices(tmp_path: Path) -> None:
    hwmon_root = tmp_path / "hwmon"
    create_hwmon_device(hwmon_root, directory="hwmon0", name="other_sensor")
    create_hwmon_device(
        hwmon_root,
        directory="hwmon4",
        temperature="-1250",
        humidity="50875",
    )

    sensor = SHT31(hwmon_root=hwmon_root)

    assert sensor.get_temp_and_humidity() == pytest.approx((-1.25, 50.875))


def test_raises_when_no_sht3x_device_is_found(tmp_path: Path) -> None:
    hwmon_root = tmp_path / "hwmon"
    create_hwmon_device(hwmon_root, name="other_sensor")

    with pytest.raises(SHT31ReadError, match="sht3x"):
        SHT31(hwmon_root=hwmon_root)


def test_raises_when_hwmon_root_does_not_exist(tmp_path: Path) -> None:
    with pytest.raises(SHT31ReadError, match="hwmon"):
        SHT31(hwmon_root=tmp_path / "missing")


def test_raises_when_multiple_sht3x_devices_are_found(tmp_path: Path) -> None:
    hwmon_root = tmp_path / "hwmon"
    create_hwmon_device(hwmon_root, directory="hwmon1")
    create_hwmon_device(hwmon_root, directory="hwmon2")

    with pytest.raises(SHT31ReadError, match="multiple"):
        SHT31(hwmon_root=hwmon_root)


@pytest.mark.parametrize(
    ("attribute", "temperature", "humidity"),
    [
        ("temp1_input", None, "48300"),
        ("humidity1_input", "21500", None),
    ],
)
def test_raises_when_required_attribute_is_missing(
    tmp_path: Path,
    attribute: str,
    temperature: str | None,
    humidity: str | None,
) -> None:
    hwmon_root = tmp_path / "hwmon"
    device_path = hwmon_root / "hwmon0"
    device_path.mkdir(parents=True)
    (device_path / "name").write_text("sht3x", encoding="utf-8")
    if temperature is not None:
        (device_path / "temp1_input").write_text(temperature, encoding="utf-8")
    if humidity is not None:
        (device_path / "humidity1_input").write_text(humidity, encoding="utf-8")

    sensor = SHT31(hwmon_root=hwmon_root)

    with pytest.raises(SHT31ReadError, match=attribute):
        sensor.get_temp_and_humidity()


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("temp1_input", "not-a-number"),
        ("humidity1_input", ""),
        ("temp1_input", "21.5"),
    ],
)
def test_raises_when_attribute_value_is_not_an_integer(
    tmp_path: Path, attribute: str, value: str
) -> None:
    hwmon_root = tmp_path / "hwmon"
    device_path = create_hwmon_device(hwmon_root)
    (device_path / attribute).write_text(value, encoding="utf-8")
    sensor = SHT31(hwmon_root=hwmon_root)

    with pytest.raises(SHT31ReadError, match=attribute):
        sensor.get_temp_and_humidity()


def test_raises_with_context_when_attribute_cannot_be_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    hwmon_root = tmp_path / "hwmon"
    device_path = create_hwmon_device(hwmon_root)
    attribute_path = device_path / "humidity1_input"
    original_read_text = Path.read_text

    def read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path == attribute_path:
            raise PermissionError("permission denied")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    sensor = SHT31(hwmon_root=hwmon_root)

    with pytest.raises(SHT31ReadError, match="humidity1_input"):
        sensor.get_temp_and_humidity()
