import pytest
from datetime import timedelta
try:
    from pyummeter import UMmeterInterfaceBT
except ImportError:
    pass


@pytest.fixture
def mock_socket(mocker):
    return mocker.patch("socket.socket", autospec=True)


class TestInterfaceBT:
    def test_init(self, mock_socket):
        with pytest.raises(AssertionError):
            UMmeterInterfaceBT(None)  # type: ignore
        with pytest.raises(AssertionError):
            UMmeterInterfaceBT("")
        UMmeterInterfaceBT("11:22:33:44:55:66").open()
        mock_socket.assert_called_once()

    def test_open_close(self, mock_socket):
        interface = UMmeterInterfaceBT("11:22:33:44:55:66")
        # TTY initialised, but not opened.
        mock_socket.assert_not_called()
        assert not interface.is_open()
        # Open TTY, first time => create serial instance.
        interface.open()
        mock_socket.assert_called_once()
        mock_socket.return_value.connect.assert_called_once()
        assert interface.is_open()
        # Close TTY.
        interface.close()
        mock_socket.return_value.close.assert_called_once()
        assert not interface.is_open()
        # Open TTY, second time => instance created, just open serial.
        interface.open()
        mock_socket.assert_called_once()
        mock_socket.return_value.connect.assert_called()
        assert interface.is_open()
        # Close TTY.
        interface.close()
        mock_socket.return_value.close.assert_called()
        assert not interface.is_open()

    def test_set_timeout(self, mock_socket):
        interface = UMmeterInterfaceBT("11:22:33:44:55:66")
        interface.open()
        interface.set_timeout(timedelta(seconds=10))
        mock_socket.return_value.settimeout.assert_called_once_with(10.0)

    def test_set_timeout_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceBT("11:22:33:44:55:66").set_timeout(timedelta(seconds=1))

    def test_send_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceBT("11:22:33:44:55:66").send(bytearray([1]))

    def test_receive_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceBT("11:22:33:44:55:66").receive(1)

    def test_send(self, mock_socket):
        data = bytearray([0xff, 0x55])
        mock_socket.return_value.send.return_value = len(data)
        interface = UMmeterInterfaceBT("11:22:33:44:55:66")
        interface.open()
        assert interface.send(data) == 2
        mock_socket.return_value.send.assert_called_with(data)

    def test_receive(self, mock_socket):
        data = bytearray([0xaa, 0xff])
        mock_socket.return_value.recv.return_value = data
        interface = UMmeterInterfaceBT("11:22:33:44:55:66")
        interface.open()
        assert interface.receive(2) == data
        mock_socket.return_value.recv.assert_called_once()
