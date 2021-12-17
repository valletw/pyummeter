from datetime import timedelta
import pytest
from src.ummeter import UMmeter


@pytest.fixture
def serial(mocker):
    return mocker.patch("serial.Serial", autospec=True)


class TestUMmeter:
    def test_init(self, serial):
        with pytest.raises(AssertionError):
            UMmeter(None)
        with pytest.raises(AssertionError):
            UMmeter("")
        with UMmeter("/dev/tty"):
            pass
        serial.assert_called_once_with(
            "/dev/tty", baudrate=9600, bytesize=8, parity='N', stopbits=1)

    def test_str(self):
        assert str(UMmeter("/dev/tty")) == "<UM-Meter: tty=/dev/tty open=False>"

    def test_open(self):
        with pytest.raises(IOError):
            with UMmeter("/dev/null"):
                pass

    def test_enter_exit_1(self, serial):
        with UMmeter("/dev/tty") as meter:
            assert meter is not None
            assert meter.is_open()
            serial.assert_called_once()
            serial.return_value.close.assert_not_called()
        assert not meter.is_open()
        serial.return_value.close.assert_called_once()

    def test_enter_exit_2(self, serial):
        meter = UMmeter("/dev/tty")
        # TTY initialised, but not opened.
        serial.assert_not_called()
        assert not meter.is_open()
        # Open TTY, first time => create serial instance.
        with meter:
            serial.assert_called_once()
            serial.return_value.open.assert_not_called()
            assert meter.is_open()
        # Close TTY.
        serial.return_value.close.assert_called_once()
        assert not meter.is_open()
        # Open TTY, second time => instance created, just open serial.
        with meter:
            serial.assert_called_once()
            serial.return_value.open.assert_called_once()
            assert meter.is_open()
        # Close TTY.
        serial.return_value.close.assert_called()
        assert not meter.is_open()

    def test_set_timeout(self, serial):
        with UMmeter("/dev/tty") as meter:
            meter.set_timeout(1)
        serial.assert_called_once()
        assert serial.return_value.timeout == 1

    def test_set_timeout_closed(self, serial):
        with pytest.raises(IOError):
            UMmeter("/dev/tty").set_timeout(1)

    def test_send_closed(self, serial):
        with pytest.raises(IOError):
            UMmeter("/dev/tty")._send(bytearray([1]))

    def test_receive_closed(self, serial):
        with pytest.raises(IOError):
            UMmeter("/dev/tty")._receive(1)

    def test_control(self, serial):
        with UMmeter("/dev/tty") as meter:
            meter.screen_next()
            serial.return_value.write.assert_called_with(bytearray([0xf1]))
            meter.screen_previous()
            serial.return_value.write.assert_called_with(bytearray([0xf3]))
            meter.screen_rotate()
            serial.return_value.write.assert_called_with(bytearray([0xf2]))
            with pytest.raises(ValueError):
                meter.screen_timeout(-1)
            with pytest.raises(ValueError):
                meter.screen_timeout(10)
            meter.screen_timeout(0)
            serial.return_value.write.assert_called_with(bytearray([0xe0]))
            meter.screen_timeout(9)
            serial.return_value.write.assert_called_with(bytearray([0xe9]))
            with pytest.raises(ValueError):
                meter.screen_brightness(-1)
            with pytest.raises(ValueError):
                meter.screen_brightness(6)
            meter.screen_brightness(0)
            serial.return_value.write.assert_called_with(bytearray([0xd0]))
            meter.screen_brightness(5)
            serial.return_value.write.assert_called_with(bytearray([0xd5]))
            meter.data_group_next()
            serial.return_value.write.assert_called_with(bytearray([0xf3]))
            meter.data_group_clear()
            serial.return_value.write.assert_called_with(bytearray([0xf4]))
            with pytest.raises(ValueError):
                meter.data_group_set(-1)
            with pytest.raises(ValueError):
                meter.data_group_set(10)
            meter.data_group_set(0)
            serial.return_value.write.assert_called_with(bytearray([0xa0]))
            meter.data_group_set(9)
            serial.return_value.write.assert_called_with(bytearray([0xa9]))
            with pytest.raises(ValueError):
                meter.data_threshold(-1)
            with pytest.raises(ValueError):
                meter.data_threshold(301)
            meter.data_threshold(0)
            serial.return_value.write.assert_called_with(bytearray([0xb0]))
            meter.data_threshold(12)
            serial.return_value.write.assert_called_with(bytearray([0xb1]))
            meter.data_threshold(16)
            serial.return_value.write.assert_called_with(bytearray([0xb2]))
            meter.data_threshold(300)
            serial.return_value.write.assert_called_with(bytearray([0xce]))

    def test_get_data_empty(self, serial):
        with UMmeter("/dev/tty") as meter:
            assert meter.get_data() is None

    def test_get_data_unknown(self, serial):
        serial.return_value.read.return_value = bytearray([
            0xff, 0xff, 0x01, 0xfe, 0x01, 0x48, 0x00, 0x00,     # Offset   0:  7
            0x06, 0x88, 0x00, 0x14, 0x00, 0x44, 0x00, 0x08,     # Offset   8: 15
            0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x38,     # Offset  16: 23
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  24: 31
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  32: 39
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  40: 47
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  48: 55
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  56: 63
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  64: 71
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  72: 79
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  80: 87
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  88: 95
            0x00, 0x01, 0x00, 0x02, 0x00, 0xff, 0x00, 0x00,     # Offset  96:103
            0x00, 0x10, 0x00, 0x00, 0x01, 0x00, 0x00, 0x0a,     # Offset 104:111
            0x00, 0x00, 0x00, 0xf0, 0x00, 0x00, 0x00, 0x02,     # Offset 112:119
            0x00, 0x04, 0x00, 0x01, 0x86, 0x9f, 0x00, 0x02,     # Offset 120:127
            0x68, 0x8c                                          # Offset 128:129
        ])
        with UMmeter("/dev/tty") as meter:
            data = meter.get_data()
            serial.return_value.write.assert_called_with(bytearray([0xf0]))
            serial.return_value.read.assert_called_once()
            assert data == {
                "model": "Unknown",
                "voltage": 0.0,
                "intensity": 0.0,
                "power": 0.0,
                "resistance": 0.0,
                "usb_voltage_dp": 0.0,
                "usb_voltage_dn": 0.0,
                "charging_mode": "Unknown",
                "charging_mode_full": "Unknown",
                "temperature_celsius": 20,
                "temperature_fahrenheit": 68,
                "data_group_selected": 8,
                "data_group": [
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0}
                ],
                "record_capacity_threshold": 0.0,
                "record_energy_threshold": 0.0,
                "record_intensity_threshold": 0.0,
                "record_duration": timedelta(seconds=240),
                "record_enabled": False,
                "screen_index": 2,
                "screen_timeout": timedelta(minutes=2),
                "screen_brightness": 4,
                "checksum": 0x8c,
            }

    def test_get_data_um25c_model(self, serial):
        serial.return_value.read.return_value = bytearray([
            0x09, 0xc9, 0x01, 0xfe, 0x01, 0x48, 0x00, 0x00,     # Offset   0:  7
            0x06, 0x88, 0x00, 0x14, 0x00, 0x44, 0x00, 0x08,     # Offset   8: 15
            0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x38,     # Offset  16: 23
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  24: 31
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  32: 39
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  40: 47
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  48: 55
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  56: 63
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  64: 71
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  72: 79
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  80: 87
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  88: 95
            0x00, 0x01, 0x00, 0x02, 0x00, 0x07, 0x00, 0x00,     # Offset  96:103
            0x00, 0x10, 0x00, 0x00, 0x01, 0x00, 0x00, 0x0a,     # Offset 104:111
            0x00, 0x00, 0x00, 0xf0, 0x00, 0x00, 0x00, 0x02,     # Offset 112:119
            0x00, 0x04, 0x00, 0x01, 0x86, 0x9f, 0x00, 0x02,     # Offset 120:127
            0x68, 0x8c                                          # Offset 128:129
        ])
        with UMmeter("/dev/tty") as meter:
            data = meter.get_data()
            serial.return_value.write.assert_called_with(bytearray([0xf0]))
            serial.return_value.read.assert_called_once()
            assert data == {
                "model": "UM25C",
                "voltage": 0.51,
                "intensity": 0.0328,
                "power": 1.672,
                "resistance": 9999.9,
                "usb_voltage_dp": 0.01,
                "usb_voltage_dn": 0.02,
                "charging_mode": "DCP1.5A",
                "charging_mode_full": "Dedicated Charging Port (max. 1.5 A)",
                "temperature_celsius": 20,
                "temperature_fahrenheit": 68,
                "data_group_selected": 8,
                "data_group": [
                    {"capacity": 0.011, "energy": 0.056},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0}
                ],
                "record_capacity_threshold": 0.016,
                "record_energy_threshold": 0.256,
                "record_intensity_threshold": 0.1,
                "record_duration": timedelta(seconds=240),
                "record_enabled": False,
                "screen_index": 2,
                "screen_timeout": timedelta(minutes=2),
                "screen_brightness": 4,
                "checksum": 0x8c,
            }

    def test_get_data_um34c_model(self, serial):
        serial.return_value.read.return_value = bytearray([
            0x0d, 0x4c, 0x01, 0xfe, 0x01, 0x48, 0x00, 0x00,     # Offset   0:  7
            0x06, 0x88, 0x00, 0x14, 0x00, 0x44, 0x00, 0x08,     # Offset   8: 15
            0x00, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x38,     # Offset  16: 23
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  24: 31
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  32: 39
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  40: 47
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  48: 55
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  56: 63
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  64: 71
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  72: 79
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  80: 87
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Offset  88: 95
            0x00, 0x01, 0x00, 0x02, 0x00, 0x07, 0x00, 0x00,     # Offset  96:103
            0x00, 0x10, 0x00, 0x00, 0x01, 0x00, 0x00, 0x0a,     # Offset 104:111
            0x00, 0x00, 0x00, 0xf0, 0x00, 0x00, 0x00, 0x02,     # Offset 112:119
            0x00, 0x04, 0x00, 0x01, 0x86, 0x9f, 0x00, 0x02,     # Offset 120:127
            0x68, 0x8c                                          # Offset 128:129
        ])
        with UMmeter("/dev/tty") as meter:
            data = meter.get_data()
            serial.return_value.write.assert_called_with(bytearray([0xf0]))
            serial.return_value.read.assert_called_once()
            assert data == {
                "model": "UM34C",
                "voltage": 5.10,
                "intensity": 0.328,
                "power": 1.672,
                "resistance": 9999.9,
                "usb_voltage_dp": 0.01,
                "usb_voltage_dn": 0.02,
                "charging_mode": "DCP1.5A",
                "charging_mode_full": "Dedicated Charging Port (max. 1.5 A)",
                "temperature_celsius": 20,
                "temperature_fahrenheit": 68,
                "data_group_selected": 8,
                "data_group": [
                    {"capacity": 0.011, "energy": 0.056},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0},
                    {"capacity": 0.0, "energy": 0.0}
                ],
                "record_capacity_threshold": 0.016,
                "record_energy_threshold": 0.256,
                "record_intensity_threshold": 0.1,
                "record_duration": timedelta(seconds=240),
                "record_enabled": False,
                "screen_index": 2,
                "screen_timeout": timedelta(minutes=2),
                "screen_brightness": 4,
                "checksum": 0x8c,
            }
