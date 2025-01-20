from serial.tools import list_ports
import pydobot
from svgpathtools import svg2paths
import numpy as np



device = pydobot.Dobot(port='/dev/tty.usbserial-0001', verbose=True)

svg_file_path = "raccoon.svg"



def svg_to_coordinates(svg_file, resolution=100):
    paths, attributes = svg2paths(svg_file)
    coordinates = []
    for path in paths:
        for i in np.linspace(0, 1, resolution):
            point = path.point(i)
            coordinates.append((point.real, point.imag))
    return coordinates

def reduce_points(coords, max_points):
    if len(coords) > max_points:
        indices = np.linspace(0, len(coords) - 1, max_points, dtype=int)
        return [coords[i] for i in indices]
    return coords

def center_and_scale_coordinates(coords, target_x_min, target_x_max, target_y_min, target_y_max):
    x_vals = [x for x, y in coords]
    y_vals = [y for x, y in coords]
    
    original_x_min, original_x_max = min(x_vals), max(x_vals)
    original_y_min, original_y_max = min(y_vals), max(y_vals)
    
    original_width = original_x_max - original_x_min
    original_height = original_y_max - original_y_min
    target_width = target_x_max - target_x_min
    target_height = target_y_max - target_y_min
    
    scale_factor = min(target_width / original_width, target_height / original_height)
    
    scaled_coords = [
        (
            (x - original_x_min) * scale_factor + target_x_min,
            (y - original_y_min) * scale_factor + target_y_min
        )
        for x, y in coords
    ]
    
    center_x = (target_x_min + target_x_max) / 2
    center_y = (target_y_min + target_y_max) / 2
    
    scaled_center_x = (min(x for x, y in scaled_coords) + max(x for x, y in scaled_coords)) / 2
    scaled_center_y = (min(y for x, y in scaled_coords) + max(y for x, y in scaled_coords)) / 2
    
    dx = center_x - scaled_center_x
    dy = center_y - scaled_center_y
    
    centered_coords = [(x + dx, y + dy) for x, y in scaled_coords]
    return centered_coords


coords = svg_to_coordinates(svg_file_path, resolution=100)

reduced_coords = reduce_points(coords, max_points=2000)

target_x_min, target_x_max = 200, 300
target_y_min, target_y_max = -75, 75

centered_coords = center_and_scale_coordinates(reduced_coords, target_x_min, target_x_max, target_y_min, target_y_max)

with open("coordinates.txt", "w") as f:
    for x, y in centered_coords:
        f.write(f"{x}, {y}\n")


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

device.move_to(200, -75, -48.2, 0, wait=False)

coords = svg_to_coordinates(svg_file_path, resolution=100)

scaled_coords = transform_coordinates(coords, scale=0.1) 

current_x, current_y, z, r, j1, j2, j3, j4 = device.pose()

z_draw_height = z  
for dx, dy in scaled_coords:
    target_x = current_x + dx
    target_y = current_y + dy
    device.move_to(target_x, target_y, z_draw_height, r, wait=False)

device.close() 


