""" CSV export manager """
import csv
from datetime import datetime, timedelta
from typing import Callable, Optional
from pyummeter import UMmeterData


def _bool_to_str(value: bool) -> str:
    """ Convert bool to string """
    return str(int(value))


def _datetime_to_str(value: datetime) -> str:
    """ Convert date to string (ISO format) """
    return value.isoformat(sep=" ")


def _timedelta_to_str(value: timedelta) -> str:
    """ Convert time delta to string (elapsing seconds) """
    return str(int(value.total_seconds()))


class ExportCSV:
    """ CSV export instance """
    _SEP = ";"
    _FIELD_DATE = ("", "Date", _datetime_to_str)
    _FIELDS = [
        # UM-Meter field, Description, Conversion method.
        ("voltage", "Voltage (V)", None),
        ("intensity", "Intensity (A)", None),
        ("power", "Power (W)", None),
        ("resistance", "Resistance (Ohm)", None),
        ("usb_voltage_dp", "USB D+ (V)", None),
        ("usb_voltage_dn", "USB D- (V)", None),
        ("charging_mode", "Charging Mode", None),
        ("temperature_celsius", "Temperature (°C)", None),
        ("model", "Model", None),
        ("record_enabled", "Recording", _bool_to_str),
        ("record_duration", "Record duration (sec)", _timedelta_to_str),
        ("record_intensity_threshold", "Record intensity (A)", None),
        ("record_capacity_threshold", "Record capacity (Ah)", None),
        ("record_energy_threshold", "Record energy (Wh)", None),
    ]
    _FIELDS_DG = [
        # UM-Meter field, Description.
        ("capacity", "Capacity (Ah)", None),
        ("energy", "Energy (Wh)", None),
    ]

    def __init__(self, filename: str):
        assert filename is not None
        assert len(filename) != 0
        self._path = filename
        # Prepare description row.
        desc_row = [self._FIELD_DATE[1]]
        desc_row.extend([d[1] for d in self._FIELDS])
        desc_row.extend([d[1] for d in self._FIELDS_DG])
        # Write description row, and create CSV file.
        with open(self._path, "w", encoding="utf-8") as csv_f:
            csv_w = csv.writer(
                csv_f, delimiter=self._SEP, quoting=csv.QUOTE_MINIMAL)
            csv_w.writerow(desc_row)

    def __str__(self):
        return f"<ExportCSV: path={self._path}>"

    @staticmethod
    def _convert(convert: Optional[Callable], value) -> str:
        if convert is None:
            return str(value)
        return convert(value)

    def update(self, date: datetime, data: UMmeterData):
        """ Write data to export file """
        # Prepare values to export.
        val = [
            self._convert(self._FIELD_DATE[2], date)
        ]
        val.extend([
            self._convert(f[2], data[f[0]])  # type: ignore
            for f in self._FIELDS
        ])
        val.extend([
            self._convert(
                f[2],
                data["data_group"][data["data_group_selected"]][f[0]])  # type: ignore
            for f in self._FIELDS_DG
        ])
        # Write value to CSV file.
        with open(self._path, "a", encoding="utf-8") as csv_f:
            csv_w = csv.writer(
                csv_f, delimiter=self._SEP, quoting=csv.QUOTE_MINIMAL)
            csv_w.writerow(val)
