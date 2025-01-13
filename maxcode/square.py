from serial.tools import list_ports
import pydobot
device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)

(x, y, z, r, j1, j2, j3, j4) = device.pose()
print(f'Initial position - x: {x}, y: {y}, z: {z}, r: {r}')

p1 = (x, y, z)          
p2 = (x + 50, y, z)     
p3 = (x + 50, y + 50, z)
p4 = (x, y + 50, z)      
device.move_to(*p1, r, wait=True)

for i in range (1000):
    device.move_to(*p2, r, wait=True) 
    device.move_to(*p3, r, wait=True)
    device.move_to(*p4, r, wait=True) 
    device.move_to(*p1, r, wait=True)  

device.close()
