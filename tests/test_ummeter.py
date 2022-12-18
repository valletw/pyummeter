from datetime import timedelta
from unittest.mock import Mock
import pytest
from pyummeter import UMmeter, UMmeterInterface


@pytest.fixture
def mock_interface():
    return Mock(spec=UMmeterInterface)


class TestUMmeter:
    def test_enter_exit(self, mock_interface):
        with UMmeter(mock_interface):
            mock_interface.open.assert_called_once()
        mock_interface.close.assert_called_once()

    def test_set_timeout(self, mock_interface):
        # Closed
        mock_interface.is_open.return_value = False
        UMmeter(mock_interface).set_timeout(1)
        mock_interface.set_timeout.assert_not_called()
        # Open
        mock_interface.is_open.return_value = True
        UMmeter(mock_interface).set_timeout(1)
        mock_interface.set_timeout.assert_called_once()

    def test_control(self, mock_interface):
        mock_interface.is_open.return_value = True
        meter = UMmeter(mock_interface)
        meter.screen_next()
        mock_interface.send.assert_called_with(bytearray([0xf1]))
        meter.screen_previous()
        mock_interface.send.assert_called_with(bytearray([0xf3]))
        meter.screen_rotate()
        mock_interface.send.assert_called_with(bytearray([0xf2]))
        with pytest.raises(ValueError):
            meter.screen_timeout(-1)
        with pytest.raises(ValueError):
            meter.screen_timeout(10)
        meter.screen_timeout(0)
        mock_interface.send.assert_called_with(bytearray([0xe0]))
        meter.screen_timeout(9)
        mock_interface.send.assert_called_with(bytearray([0xe9]))
        with pytest.raises(ValueError):
            meter.screen_brightness(-1)
        with pytest.raises(ValueError):
            meter.screen_brightness(6)
        meter.screen_brightness(0)
        mock_interface.send.assert_called_with(bytearray([0xd0]))
        meter.screen_brightness(5)
        mock_interface.send.assert_called_with(bytearray([0xd5]))
        meter.data_group_next()
        mock_interface.send.assert_called_with(bytearray([0xf3]))
        meter.data_group_clear()
        mock_interface.send.assert_called_with(bytearray([0xf4]))
        with pytest.raises(ValueError):
            meter.data_group_set(-1)
        with pytest.raises(ValueError):
            meter.data_group_set(10)
        meter.data_group_set(0)
        mock_interface.send.assert_called_with(bytearray([0xa0]))
        meter.data_group_set(9)
        mock_interface.send.assert_called_with(bytearray([0xa9]))
        with pytest.raises(ValueError):
            meter.data_threshold(-1)
        with pytest.raises(ValueError):
            meter.data_threshold(301)
        meter.data_threshold(0)
        mock_interface.send.assert_called_with(bytearray([0xb0]))
        meter.data_threshold(12)
        mock_interface.send.assert_called_with(bytearray([0xb1]))
        meter.data_threshold(16)
        mock_interface.send.assert_called_with(bytearray([0xb2]))
        meter.data_threshold(300)
        mock_interface.send.assert_called_with(bytearray([0xce]))

    def test_get_data_empty(self, mock_interface):
        mock_interface.is_open.return_value = True
        mock_interface.receive.return_value = bytearray()
        UMmeter(mock_interface).get_data() is None

    def test_get_data_unknown(self, mock_interface):
        mock_interface.is_open.return_value = True
        mock_interface.receive.return_value = bytearray([
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
        data = UMmeter(mock_interface).get_data()
        mock_interface.send.assert_called_with(bytearray([0xf0]))
        mock_interface.receive.assert_called_once()
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

    def test_get_data_um25c_model(self, mock_interface):
        mock_interface.is_open.return_value = True
        mock_interface.receive.return_value = bytearray([
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
        data = UMmeter(mock_interface).get_data()
        mock_interface.send.assert_called_with(bytearray([0xf0]))
        mock_interface.receive.assert_called_once()
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

    def test_get_data_um34c_model(self, mock_interface):
        mock_interface.is_open.return_value = True
        mock_interface.receive.return_value = bytearray([
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
        data = UMmeter(mock_interface).get_data()
        mock_interface.send.assert_called_with(bytearray([0xf0]))
        mock_interface.receive.assert_called_once()
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
