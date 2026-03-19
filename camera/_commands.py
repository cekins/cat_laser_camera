from . import _packets


def power_on():
    _packets.general_cmd(b'\x01\x04\x00\x02')

def power_off():
    _packets.general_cmd(b'\x01\x04\x00\x02')
