""" UM-Meter interface Bluetooth """
import socket
from datetime import timedelta
from typing import Optional
from pyummeter.interface_base import UMmeterInterface


class UMmeterInterfaceBT(UMmeterInterface):
    def __init__(self, mac: str):
        assert mac is not None
        assert len(mac) != 0
        self._mac = mac
        # Do not open interface on init.
        self._socket: Optional[socket.socket] = None
        self._is_open = False

    def __str__(self):
        return f"<BT: path={self._mac} open={self.is_open()}>"

    def is_open(self) -> bool:
        """ Check if interface is open """
        return self._is_open

    def open(self):
        """ Open interface """
        if not self.is_open():
            try:
                if self._socket is None:
                    # No instance, create it.
                    self._socket = socket.socket(
                        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                self._socket.connect((self._mac, 1))
                self._is_open = True
            except Exception as exp:
                raise IOError("UM-Meter: could not open BT interface") from exp

    def close(self):
        """ Close interface """
        if self.is_open() and self._socket is not None:
            self._socket.close()
            self._is_open = False

    def set_timeout(self, timeout: timedelta):
        """ Configure receive timeout """
        if self._socket is None:
            raise IOError("UM-Meter: BT interface is not opened")
        self._socket.settimeout(timeout.total_seconds())

    def send(self, data: bytearray) -> int:
        """ Send raw data to interface, return number of bytes sent """
        if not self.is_open() or self._socket is None:
            raise IOError("UM-Meter: BT interface is not opened")
        return self._socket.send(bytes(data))

    def receive(self, nb: int) -> bytearray:
        """ Receive 'nb' bytes of raw data from interface, return bytes received """
        if not self.is_open() or self._socket is None:
            raise IOError("UM-Meter: BT interface is not opened")
        return bytearray(self._socket.recv(nb))
