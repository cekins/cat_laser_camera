

#TODO make this a singleton class, this is getting too disorganized

_ser = serial.Serial(**SERIAL_SETTINGS)
_ser = None

ADDRESS = 1

ADDRESS = b'\x81'
TERMINATOR = b'\xFF'


def _packet_to_str(packet: bytes):
    return packet.hex(" ")


@contextmanager
def connect(port):
    global _ser
    with serial.Serial(port=port, **SERIAL_SETTINGS) as _ser:
        _logger.debug(f'connected to camera at port {port}')
        _address_set()
        if_clear()
        yield
    _logger.debug(f'disconnected from camera at port {port}')


def _read_packet():
    packet = _ser.read_until(TERMINATOR)
    _logger.debug(f'{_packet_to_str(packet)} read from camera')
    return packet


def _write_packet_read_packet(packet: bytes):
    _ser.write(packet)
    _logger.debug(f'{_packet_to_str(packet)} written to camera')
    return _read_packet()


def _address_set():
    """TODO"""
    reply = _write_packet_read_packet(b'\x88\x30\x01\xFF')
    if reply != b'\x88\x30\x02\xFF':
        raise RuntimeError('Unexpected response while setting camera address')


def if_clear():
    """TODO"""
    reply = _write_packet_read_packet(b'\x88\x01\x00\x01\xFF')
    if reply != b'\x88\x01\x00\x01\xFF':
        raise RuntimeError('Unexpected response to if clear')


def general_cmd(cmd: bytes):
    """TODO"""
    packet = ADDRESS + cmd + TERMINATOR
    reply = _write_packet_read_packet(packet)

    # TODO add packet contents verification
    return reply[1:-1]

# Address set
# ser.write(b'\x88\x30\x01\xFF')

# Info
# ser.write(b'\x81\x09\x00\x02\xFF')


# IF clear
# ser.write(b'\x88\x01\x00\x01\xFF')

# cam_power ON
# ser.write(b'\x81\x01\x04\x00\x02\xFF')

# cam_power off
# ser.write(b'\x81\x01\x04\x00\x03\xFF')


# out = ser.read_until(b'\xFF')

# print(out)
