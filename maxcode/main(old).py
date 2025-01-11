from serial.tools import list_ports
import pydobot
from svgpathtools import svg2paths
import numpy as np

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

def filter_coordinates(coords, x_min, x_max, y_min, y_max):
    return [(x, y) for x, y in coords if x_min <= x <= x_max and y_min <= y <= y_max]

device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)

svg_file_path = "raccoon.svg"
coords = svg_to_coordinates(svg_file_path, resolution=100)

scaled_coords = transform_coordinates(coords, scale=0.1, offset=(200, 200))

x_min, x_max = 200, 300
y_min, y_max = -100, 100

filtered_coords = filter_coordinates(scaled_coords, x_min, x_max, y_min, y_max)

z_draw_height = 10

if filtered_coords:
    start_x, start_y = filtered_coords[0]
    device.move_to(start_x, start_y, z_draw_height, r=0, wait=True)

    for x, y in filtered_coords:
        device.move_to(x, y, z_draw_height, r=0, wait=False)

device.close()