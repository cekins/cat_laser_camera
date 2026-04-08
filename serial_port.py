from serial.tools import list_ports


def get_port(conf: dict):
    pid = conf['camera']['pid']
    vid = conf['camera']['vid']

    matching_ports = []
    for port in list_ports.comports():
        if port.pid == pid and port.vid == vid:
            matching_ports.append(port.device)

    if len(matching_ports) == 0:
        raise RuntimeError('Failed to find camera port')
    if len(matching_ports) > 1:
        raise RuntimeError(f'Found too many matching camera ports: {matching_ports}')

    return matching_ports[0]
