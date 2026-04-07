import serial
import logging
import time

_logger = logging.getLogger(__name__)

_SERIAL_SETTINGS = {
    'baudrate': 38400,
    'bytesize': serial.EIGHTBITS,
    'parity': serial.PARITY_NONE,
    'stopbits': serial.STOPBITS_ONE,
    'xonxoff': False,
    'rtscts': False,
    'write_timeout': None,
    'dsrdtr': True,
    'inter_byte_timeout': None
}

_BROADCAST_ADDRESS_BYTE = b'\x88'
_CAMERA_ADDRESS_BYTE = b'\x81'
_CAMERA_REPLY_ADDRESS_BYTE = b'\x90'

_PACKET_TERMINATION_BYTE = b'\xFF'

_ACK_TIMEOUT = 1


def _packet_to_str(packet: bytes) -> str:
    """TODO"""
    return f"[{packet.hex(' ')}]"


class SerialConnection:

    def __init__(self, port):
        self._ser = serial.Serial(**_SERIAL_SETTINGS)
        self._ser.port = port

    def __enter__(self):
        self._ser.open()
        # TODO where do these buffer resets go
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

        # Start by setting address and executing IF clear as per manual instructions
        self.address_set()
        self.broadcast_if_clear()

        return self

    def __exit__(self, *_):
        self._ser.close()

    def _read_packet(self, timeout) -> bytes:
        """Reads a packet from the camera"""

        timeout = time.time() + timeout
        packet_data = b''
        while timeout > time.time():
            if self._ser.in_waiting > 0:
                next_byte = self._ser.read(1)
                if next_byte == _PACKET_TERMINATION_BYTE:
                    _logger.debug(f'{_packet_to_str(next_byte)} received from camera')
                    return packet_data
                packet_data += next_byte

        raise RuntimeError('Timeout while reading packet from camera')

    def _write_packet(self, packet_data: bytes) -> bytes:
        packet = packet_data + _PACKET_TERMINATION_BYTE
        self._ser.write(packet)
        _logger.debug(f'{_packet_to_str(packet)} written to camera')
        return self._read_packet(_ACK_TIMEOUT)

    def _send_broadcast_command(self, command):
        """TODO"""
        reply_packet_data = self._write_packet(_BROADCAST_ADDRESS_BYTE + command)
        if reply_packet_data[0:1] != _BROADCAST_ADDRESS_BYTE:
            raise RuntimeError(f'Broadcast command returned non-broadcast addressed reply')
        return reply_packet_data[1:]

    def _send_addressed_command(self, command):
        """TODO"""
        reply_packet_data = self._write_packet(_CAMERA_ADDRESS_BYTE + command)
        if reply_packet_data[0:1] != _BROADCAST_ADDRESS_BYTE:
            raise RuntimeError(f'Addressed command returned incorrectly addressed reply')
        return reply_packet_data[1:]

    def address_set(self):
        """TODO"""
        reply_packet_data = self._send_broadcast_command(b'\x30\x01')
        if reply_packet_data != b'\x30\x02':
            raise RuntimeError('Unexpected response while setting camera address')

    def broadcast_if_clear(self):
        """TODO"""
        reply_packet_data = self._send_broadcast_command(b'\x01\x00\x01')
        if reply_packet_data != b'\x01\x00\x01':
            raise RuntimeError('Unexpected response after executing broadcast IF clear')
