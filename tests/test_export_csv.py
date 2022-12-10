import pytest
import unittest
from datetime import datetime, timedelta
from pyummeter import UMmeterData
from pyummeter.export_csv import ExportCSV


@pytest.fixture
def mfile(mocker):
    return mocker.patch("builtins.open", unittest.mock.mock_open())


class TestExportCSV:
    def test_init(self, mfile):
        with pytest.raises(AssertionError):
            ExportCSV(None)
        with pytest.raises(AssertionError):
            ExportCSV("")
        export = ExportCSV("test.csv")
        mfile().write.assert_called_once()
        mfile().write.assert_called_with(
            "Date;Voltage (V);Intensity (A);Power (W);Resistance (Ohm);USB D+ (V);"
            "USB D- (V);Charging Mode;Temperature (°C);Model;Recording;"
            "Record duration (sec);Record intensity (A);Record capacity (Ah);"
            "Record energy (Wh);Capacity (Ah);Energy (Wh)\r\n")
        assert str(export) == "<ExportCSV: path=test.csv>"

    def test_update(self, mfile):
        date = datetime.now()
        data: UMmeterData = {
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
            "data_group_selected": 0,
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
        export = ExportCSV("test.csv")
        mfile().reset_mock()
        export.update(date, data)
        mfile().write.assert_called_once()
        mfile().write.assert_called_with(
            f"{date.isoformat(sep=' ')};"
            "5.1;0.328;1.672;9999.9;0.01;0.02;DCP1.5A;20;UM34C;0;240;0.1;"
            "0.016;0.256;0.011;0.056\r\n"
        )
