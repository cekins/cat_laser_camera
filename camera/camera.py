import serial
import time
import logging

_logger = logging.getLogger(__name__)

_SERIAL_SETTINGS = {
    'baudrate': 38400,
    'bytesize': serial.EIGHTBITS,
    'parity': serial.PARITY_NONE,
    'stopbits': serial.STOPBITS_ONE,
    'timeout': 0.5,
    'xonxoff': False,
    'rtscts': False,
    'write_timeout': None,
    'dsrdtr': True,
    'inter_byte_timeout': None
}

_WRITE_ADDRESS = b'\x81'
_READ_ADDRESS = b'\x90'

_TERMINATOR = b'\xFF'

_ACKNOWLEDGE = b'\x90\x41'
_ERRORS = {
    b'\x60\x02': 'Syntax Error',
    b'\x60\x03': 'Command Buffer Full',
    b'\x60\x04': 'Command Cancelled',
    b'\x60\x05': 'No Socket',
    b'\x60\x41': 'Command Not Executable',
}


# TODO switch config to toml

def _packet_to_str(packet: bytes) -> str:
    """TODO"""
    return f"[{packet.hex(' ')}]"


class Camera:

    def __init__(self, port):
        self._ser = serial.Serial(**_SERIAL_SETTINGS)
        self._ser.port = port

    def __enter__(self):
        self._ser.open()
        return self

    def __exit__(self, *_):
        self._ser.close()

    def _read_packet(self) -> bytes:
        packet = self._ser.read_until(_TERMINATOR)
        _logger.debug(f'{_packet_to_str(packet)} read from camera')
        return packet[1:-1]

    def _write_packet(self, data: bytes) -> bytes:
        packet = _ACKNOWLEDGE + data + _TERMINATOR
        self._ser.write(packet)
        _logger.debug(f'{_packet_to_str(packet)} written to camera')
        return self._read_packet()

    def address_set(self):
        """TODO"""
        reply = self._write_packet(b'\x88\x30\x01\xFF')
        if reply != b'\x88\x30\x02\xFF':
            raise RuntimeError('Unexpected response while setting camera address')

    def if_clear(self):
        """TODO"""
        reply = self._write_packet(b'\x88\x01\x00\x01\xFF')
        if reply != b'\x88\x01\x00\x01\xFF':
            raise RuntimeError('Unexpected response to if clear')

    def _general_cmd(self, cmd: bytes):
        """TODO"""
        packet = _WRITE_ADDRESS + cmd + _TERMINATOR
        reply = self._write_packet(packet)

        # read acknowledge
        if reply != _ACKNOWLEDGE:
            if reply in _ERRORS:
                raise RuntimeError(f'Camera generated error {_ERRORS[reply]}')
            raise RuntimeError(f'Camera returned unexpected ACKNOWLEDGE')

        # wait for completion
        reply = bytes()
        end_time = time.time() + 20
        while reply != b'\x90\x51\xFF':
            if self._ser.in_waiting > 0:
                reply += self._ser.read()
            if time.time() > end_time:
                raise RuntimeError('Did not receive COMPLETION from camera')

    def power_on(self):
        self._general_cmd(b'\x01\x04\x00\x02')
        _logger.debug(f'camera powered on')

    def power_off(self):
        self._general_cmd(b'\x01\x04\x00\x03')
        _logger.debug(f'camera powered off')

    def auto_focus(self):
        self._general_cmd(b'\x01\x04\x38\x02')
        _logger.debug(f'camera autofocused')

    def home(self):
        self._general_cmd(b'\x01\x06\x04')
        _logger.debug(f'camera homed')

    def reset(self):
        self._general_cmd(b'\x01\x06\x05')
        _logger.debug(f'camera homed')

    def pan_tilt_drive(self):
        self._general_cmd(b'\x01\x06\x01\x01\x03\x01')
        # TODO logger
