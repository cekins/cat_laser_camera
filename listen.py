
import time
import serial

ser = serial.Serial(port='COM5',
                    baudrate=9600,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=None,
                    xonxoff=False,
                    rtscts=False,
                    write_timeout=None,
                    dsrdtr=False,
                    inter_byte_timeout=None)
def mine():
    this = 4
test = 5
time.sleep(10)
out = b''
while ser.inWaiting() > 0:
    out += ser.read(1)
lll
if out != b'':
    print(out)
