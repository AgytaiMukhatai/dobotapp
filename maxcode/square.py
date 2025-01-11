from serial.tools import list_ports
import pydobot

# Verbindung mit dem Dobot herstellen
device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)

# Aktuelle Position abrufen
(x, y, z, r, j1, j2, j3, j4) = device.pose()
print(f'Initial position - x: {x}, y: {y}, z: {z}, r: {r}')

# Viereckpunkte relativ zur Startposition definieren
p1 = (x, y, z)           # Startpunkt (Punkt 1)
p2 = (x + 50, y, z)      # Punkt 2
p3 = (x + 50, y + 50, z) # Punkt 3
p4 = (x, y + 50, z)      # Punkt 4

# In der Luft zum Startpunkt bewegen
device.move_to(*p1, r, wait=True)

for i in range (1000):
    device.move_to(*p2, r, wait=True)  # Zu Punkt 2
    device.move_to(*p3, r, wait=True)  # Zu Punkt 3
    device.move_to(*p4, r, wait=True)  # Zu Punkt 4
    device.move_to(*p1, r, wait=True)  # Zurück zum Startpunkt

# Verbindung schließen
device.close()
