import time

import serial
import unittest

import serial_port
import log
import config

from .camera import Camera

conf = config.load_conf()
port = serial_port.get_port(conf)
log.setup_log(conf)


class Test_packets(unittest.TestCase):
    @unittest.skip
    def test_packet(self):
        with Camera(port) as camera:
            reply = camera._write_packet(b'\x88\x30\x01\xFF')
        self.assertEqual(b'\x88\x30\x02\xFF', reply)

    @unittest.skip
    def test_on_off(self):
        with Camera(port) as camera:
            camera.power_off()
            camera.power_on()

    def test_home(self):
        with Camera(port) as camera:
            camera.pan_tilt_drive()
            time.sleep(2)
            camera.home()


    @unittest.skip
    def test_reset(self):
        with Camera(port) as camera:
            camera.reset()
