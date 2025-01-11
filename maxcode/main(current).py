from serial.tools import list_ports
import pydobot
from svgpathtools import svg2paths
import numpy as np

#gives the dobot instructions based on the svg paths

def svg_to_coordinates(svg_file, resolution=100):

    paths, attributes = svg2paths(svg_file)
    coordinates = []
    for path in paths:
        for i in np.linspace(0, 1, resolution):
            point = path.point(i)
            coordinates.append((point.real, point.imag))
    
    return coordinates

def transform_coordinates(coords, scale=1.0, offset=(0, 0)):
    dx, dy = offset
    return [(x * scale + dx, y * scale + dy) for x, y in coords]

device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)
device.move_to(200, -100, -45, 0, wait=False)

svg_file_path = "raccoon.svg"
coords = svg_to_coordinates(svg_file_path, resolution=100)

scaled_coords = transform_coordinates(coords, scale=0.1) 

current_x, current_y, z, r, j1, j2, j3, j4 = device.pose()

z_draw_height = z  
for dx, dy in scaled_coords:
    target_x = current_x + dx
    target_y = current_y + dy
    device.move_to(target_x, target_y, z_draw_height, r, wait=False)


device.close() 


