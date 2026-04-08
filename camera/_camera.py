"""TODO"""
import logging

from _serial_connection import SerialConnection

_logger = logging.getLogger(__name__)




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
        # TODO where do these buffer resets go
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        return self

    def __exit__(self, *_):
        self._ser.close()

    def _read_packet(self, timeout) -> bytes:
        """Reads a packet from the camera"""
        # set the timeout for each call
        self._ser.timeout = timeout

        # read the packet
        packet = self._ser.read_until(_TERMINATOR)
        _logger.debug(f'{_packet_to_str(packet)} read from camera')

        # check for full packet
        if packet[-1:] != _TERMINATOR:
            raise RuntimeError(f'Did not receive full packet within {timeout} seconds{packet}')

        return packet

    def _write_packet(self, packet: bytes) -> bytes:
        self._ser.write(packet)
        _logger.debug(f'{_packet_to_str(packet)} written to camera')
        return self._read_packet(1)

    def address_set(self):
        """TODO"""
        reply = self._write_packet(b'\x88\x30\x01')
        if reply != b'\x88\x30\x02\xFF':
            raise RuntimeError('Unexpected response while setting camera address')

    def if_clear(self):
        """TODO"""
        reply = self._write_packet(b'\x88\x01\x00\x01\xFF')
        if reply != b'\x88\x01\x00\x01\xFF':
            raise RuntimeError('Unexpected response to if clear')

    def _send_command(self, cmd: bytes):
        """TODO"""
        command_packet = _WRITE_ADDRESS + cmd + _TERMINATOR
        ack_packet = self._write_packet(command_packet)

        # read acknowledge
        if ack_packet != _READ_ADDRESS + _ACKNOWLEDGE + _TERMINATOR:
            if ack_packet in _ERRORS:
                raise RuntimeError(f'Camera generated error {_ERRORS[ack_packet]}')
            raise RuntimeError(f'Camera returned unexpected output')

        # wait for completion
        timeout = 20
        compl_packet = self._read_packet(timeout)
        if compl_packet != _READ_ADDRESS + _COMPLETION + _TERMINATOR:
            if compl_packet in _ERRORS:
                raise RuntimeError(f'Camera generated error {_ERRORS[ack_packet]}')
            raise RuntimeError(f'Camera failed to return completion packet after {timeout}')

    def power_on(self):
        self._send_command(b'\x01\x04\x00\x02')
        _logger.debug(f'camera powered on')

    def power_off(self):
        self._send_command(b'\x01\x04\x00\x03')
        _logger.debug(f'camera powered off')

    def auto_focus(self):
        self._send_command(b'\x01\x04\x38\x02')
        _logger.debug(f'camera autofocused')

    def home(self):
        self._send_command(b'\x01\x06\x04')
        _logger.debug(f'camera homed')

    def reset(self):
        self._send_command(b'\x01\x06\x05')
        _logger.debug(f'camera homed')

    def pan_tilt_drive(self):
        self._send_command(b'\x01\x06\x01\x01\x03\x01')
        # TODO logger
