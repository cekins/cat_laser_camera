from serial.tools import list_ports


def get_port(conf: dict):
    pid = conf['camera']['pid']
    vid = conf['camera']['vid']

    for port in list_ports.comports():
        if port.pid == pid and port.vid == vid:
            return port.device
    raise RuntimeError('Failed to find camera port')
