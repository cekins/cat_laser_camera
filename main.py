import serial_port
from config import load_conf


def main():
    conf = load_conf()
    camera_port = serial_port.get_port(conf)
    camera_serial.connect(camera_port)
    camera_serial.power_off()
    camera_serial.disconnect()


if __name__ == '__main__':
    main()
