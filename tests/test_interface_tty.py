import pytest
from datetime import timedelta
from pyummeter import UMmeterInterfaceTTY


@pytest.fixture
def mock_serial(mocker):
    return mocker.patch("serial.Serial", autospec=True)


class TestInterfaceTTY:
    def test_init(self, mock_serial):
        with pytest.raises(AssertionError):
            UMmeterInterfaceTTY(None)  # type: ignore
        with pytest.raises(AssertionError):
            UMmeterInterfaceTTY("")
        UMmeterInterfaceTTY("/dev/tty").open()
        mock_serial.assert_called_once_with(
            "/dev/tty", baudrate=9600, bytesize=8, parity='N', stopbits=1)

    def test_open_close(self, mock_serial):
        interface = UMmeterInterfaceTTY("/dev/tty")
        # TTY initialised, but not opened.
        mock_serial.assert_not_called()
        assert not interface.is_open()
        # Open TTY, first time => create serial instance.
        interface.open()
        mock_serial.assert_called_once()
        mock_serial.return_value.open.assert_not_called()
        assert interface.is_open()
        # Close TTY.
        interface.close()
        mock_serial.return_value.close.assert_called_once()
        assert not interface.is_open()
        # Open TTY, second time => instance created, just open serial.
        interface.open()
        mock_serial.assert_called_once()
        mock_serial.return_value.open.assert_called_once()
        assert interface.is_open()
        # Close TTY.
        interface.close()
        mock_serial.return_value.close.assert_called()
        assert not interface.is_open()

    def test_set_timeout(self, mock_serial):
        interface = UMmeterInterfaceTTY("/dev/tty")
        interface.open()
        interface.set_timeout(timedelta(seconds=10))
        mock_serial.assert_called_once()
        assert mock_serial.return_value.timeout == 10

    def test_set_timeout_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceTTY("/dev/tty").set_timeout(timedelta(seconds=1))

    def test_send_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceTTY("/dev/tty").send(bytearray([1]))

    def test_receive_closed(self):
        with pytest.raises(IOError):
            UMmeterInterfaceTTY("/dev/tty").receive(1)

    def test_send(self, mock_serial):
        data = bytearray([0xff, 0x55])
        mock_serial.return_value.write.return_value = len(data)
        interface = UMmeterInterfaceTTY("/dev/tty")
        interface.open()
        assert interface.send(data) == 2
        mock_serial.return_value.write.assert_called_with(data)

    def test_receive(self, mock_serial):
        data = bytearray([0xaa, 0xff])
        mock_serial.return_value.read.return_value = data
        interface = UMmeterInterfaceTTY("/dev/tty")
        interface.open()
        assert interface.receive(2) == data
        mock_serial.return_value.read.assert_called_once()
