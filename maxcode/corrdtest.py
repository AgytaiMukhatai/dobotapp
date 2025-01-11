from serial.tools import list_ports

import pydobot
from xml.dom import minidom
from svg.path import parse_path



device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)

(x, y, z, r, j1, j2, j3, j4) = device.pose()
#print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')


#x=  
#y=
#z=-46



device.close()