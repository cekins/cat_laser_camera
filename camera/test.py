import time

import serial
import unittest

import serial_port
import log
import config

from ._camera import Camera
from ._serial_connection import SerialConnection

conf = config.load_conf()
port = serial_port.get_port(conf)
log.setup_log(conf)


class Test_packets(unittest.TestCase):

    def test_address_set(self):
        with SerialConnection(port) as conn:
            conn._address_set()
