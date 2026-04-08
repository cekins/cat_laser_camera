"""
A module encapsulating the serial connection to the VISCA camera
"""

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

_ACKNOWLEDGE_TIMEOUT = 1

_ACKNOWLEDGE = b'\x41'
_COMPLETION = b'\x51'
_ERRORS = {
    b'\x60\x02': 'Syntax Error',
    b'\x60\x03': 'Command Buffer Full',
    b'\x60\x04': 'Command Cancelled',
    b'\x60\x05': 'No Socket',
    b'\x60\x41': 'Command Not Executable',
}


def _packet_to_str(packet: bytes) -> str:
    """Converts a byte packet to a human-readable string"""
    return f"[{packet.hex(' ')}]"


class SerialConnection:

    def __init__(self, port):
        self._ser = serial.Serial(**_SERIAL_SETTINGS)
        self._ser.port = port

    def __enter__(self):
        self._ser.open()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

        # Start by setting address and executing IF clear as per manual instructions
        self._address_set()
        self._broadcast_if_clear()

        return self

    def __exit__(self, *_):
        self._ser.close()

    def _read_packet(self, timeout: float) -> bytes:
        """Reads a packet from the camera, does not include termination byte
        Args:
            timeout: Timeout in milliseconds to receive full packet
        Returns:
            packet not including termination byte
        """

        end_time = time.time() + timeout
        packet = b''
        while end_time > time.time():
            if self._ser.in_waiting > 0:
                next_byte = self._ser.read(1)
                if next_byte == _PACKET_TERMINATION_BYTE:
                    _logger.debug(f'{_packet_to_str(next_byte)} received from camera')
                    return packet
                packet += next_byte

        raise RuntimeError(f'Exceeded {timeout}s while reading packet from camera')

    def _write_packet(self, packet: bytes) -> None:
        """Writes packet to the camera
        Args:
            packet: packet to write to camera
        """
        terminated_packet = packet + _PACKET_TERMINATION_BYTE
        self._ser.write(terminated_packet)
        _logger.debug(f'{_packet_to_str(terminated_packet)} written to camera')

    def _wait_for_addressed_reply(self, address_byte: bytes, timeout: float):
        """TODO"""
        reply_packet = self._read_packet(timeout)
        if reply_packet[0:1] != address_byte:
            raise RuntimeError('Camera reply contained unexpected address')
        return reply_packet[1:]

    def execute_general_command(self, command: bytes, timeout:float) -> bytes:
        """TODO"""

        self._write_packet()


    def _send_command(self, command: bytes, timeout: float, is_broadcast=False, is_inquiry=False) -> bytes:

        # select addresses
        if is_broadcast:
            write_address = reply_address = _BROADCAST_ADDRESS_BYTE
        else:
            write_address = _CAMERA_ADDRESS_BYTE
            reply_address = _CAMERA_REPLY_ADDRESS_BYTE

        # write packet
        self._write_packet(write_address + command)

        # read packet
        if is_inquiry:
            reply_timeout = timeout
        else:
            reply_timeout = _ACKNOWLEDGE_TIMEOUT

        reply = self._wait_for_reply(reply_address, reply_timeout)

        # handle completion for non inquiry commands:
        if not is_inquiry:

            # check that acknowledge was received
            if reply != _ACKNOWLEDGE:
                raise RuntimeError('Camera acknowledge did not match expectation')

            # wait for completion
            reply = self._wait_for_reply(reply_address, reply_timeout)

        # check for errors
        if reply in _ERRORS:
            raise RuntimeError(f'Camera returned error {_ERRORS[reply]}')

        # check for completion for non-inquiry commands:
        if not is_inquiry:


    def _send_broadcast_command(self, command: bytes) -> bytes:
        """Sends a broadcast command to the camera and reads the reply
        Args:
            command: byte data of a command not including address byte
        Returns:
            byte data of the camera reply not including address byte
        """
        reply_packet_data = self._write_packet(_BROADCAST_ADDRESS_BYTE + command)
        if reply_packet_data[0:1] != _BROADCAST_ADDRESS_BYTE:
            raise RuntimeError(f'Broadcast command returned non-broadcast addressed reply')
        return reply_packet_data[1:]

    def _send_addressed_command(self, command: bytes) -> bytes:
        """Sends an addressed command to the camera and reads the reply
        Args:
            command: byte data of a command not including address byte
        Returns:
            byte data of the camera reply not including address byte
        """
        reply_packet_data = self._write_packet(_CAMERA_ADDRESS_BYTE + command)
        if reply_packet_data[0:1] != _CAMERA_REPLY_ADDRESS_BYTE:
            raise RuntimeError(f'Addressed command returned incorrectly addressed reply')
        return reply_packet_data[1:]

    def _wait_for_addressed_reply(self):

    def send_general_command(self, command: bytes) -> bytes:

        reply_command = reply_packet_data[1:]
        if reply_command in _ERRORS:

        return reply_packet_data[1:]

    def _address_set(self):
        """Sets the address of all attached cameras"""
        reply_packet_data = self._send_broadcast_command(b'\x30\x01')
        if reply_packet_data != b'\x30\x02':
            raise RuntimeError('Unexpected response while setting camera address')

    def _broadcast_if_clear(self):
        """Clears the command buffers of all attached cameras"""
        reply_packet_data = self._send_broadcast_command(b'\x01\x00\x01')
        if reply_packet_data != b'\x01\x00\x01':
            raise RuntimeError('Unexpected response after executing broadcast IF clear')
