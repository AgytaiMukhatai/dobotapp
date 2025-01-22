import matplotlib.pyplot as plt
from PIL import Image
import svgpathtools
import os
import subprocess
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit as st
from svgpathtools import svg2paths
import numpy as np

# Function to convert JPEG to SVG using potrace
def jpg_to_svg(jpg_file):
    """
    Converts a JPEG image to an SVG file using potrace.

    Parameters:
    - jpeg_file (str): Path to the JPEG file.

    Returns:
    - svg_file (str): Path to the generated SVG file.
    """
    # Convert JPEG to PNM format (required by potrace)
    
    pnm_file = jpg_file.replace('.jpg', '.pnm')
    svg_file = jpg_file.replace('.jpg', '.svg')
    
    
    Image.open(jpg_file).convert('L').save(pnm_file)

    # Use potrace to convert PNM to SVG
    subprocess.run(["potrace", "-s", pnm_file, "-o", svg_file])

    # Clean up the intermediate PNM file
    #os.remove(pnm_file)

    return svg_file

# Function to extract paths from SVG file
def svg_to_paths(svg_file):
    """
    Parses an SVG file and extracts drawing paths for Dobot.

    Parameters:
    - svg_file (str): Path to the SVG file.

    Returns:
    - paths (list of list of tuples): List of paths, where each path is a list of (x, y) coordinates.
    """
    svg_paths, _ = svgpathtools.svg2paths(svg_file)
    all_paths = []

    for svg_path in svg_paths:
        path_points = []
        for segment in svg_path:
            if isinstance(segment, svgpathtools.Line):
                path_points.append((segment.start.real, segment.start.imag))
                path_points.append((segment.end.real, segment.end.imag))
            elif isinstance(segment, svgpathtools.CubicBezier):
                for t in [i / 20 for i in range(21)]:  # Sample points along the curve
                    point = segment.point(t)
                    path_points.append((point.real, point.imag))
        all_paths.append(path_points)

    return all_paths


def adjust_points_to_borders(paths, min_x, max_x, min_y, max_y):
    """
    Adjusts points from paths to fit within the given borders.

    Parameters:
    - paths (list of list of tuples): List of paths, where each path is a list of (x, y) coordinates.
    - min_x (float): Minimum x-coordinate of the border.
    - max_x (float): Maximum x-coordinate of the border.
    - min_y (float): Minimum y-coordinate of the border.
    - max_y (float): Maximum y-coordinate of the border.

    Returns:
    - adjusted_paths (list of list of tuples): Paths with points adjusted to fit within the borders.
    """
    # Calculate the original bounding box of the points
    all_points = [point for path in paths for point in path]
    orig_min_x = min(point[0] for point in all_points)
    orig_max_x = max(point[0] for point in all_points)
    orig_min_y = min(point[1] for point in all_points)
    orig_max_y = max(point[1] for point in all_points)

    # Scale and shift points to fit within the new borders
    adjusted_paths = []
    for path in paths:
        adjusted_path = []
        for x, y in path:
            # Scale x and y to fit within the borders
            new_x = ((x - orig_min_x) / (orig_max_x - orig_min_x)) * (max_x - min_x) + min_x
            new_y = ((y - orig_min_y) / (orig_max_y - orig_min_y)) * (max_y - min_y) + min_y
            adjusted_path.append((new_x, new_y))
        adjusted_paths.append(adjusted_path)

    return adjusted_paths


def simplify_paths(paths, tolerance=0.1):
    """
    Simplifies paths using the Ramer-Douglas-Peucker algorithm.

    Parameters:
    - paths (list of list of tuples): List of paths to simplify.
    - tolerance (float): Tolerance for simplification (higher = more simplification).

    Returns:
    - simplified_paths (list of list of tuples): Simplified paths.
    """
    simplified_paths = []
    for path in paths:
        line = LineString(path)
        simplified_line = line.simplify(tolerance, preserve_topology=False)
        simplified_paths.append(list(simplified_line.coords))
    return simplified_paths

# Visualzie all the paths
def visualize_paths(paths, title="Adjusted Paths"):
    """
    Visualizes adjusted paths.

    Parameters:
    - paths (list of list of tuples): List of adjusted paths to visualize.
    - title (str): Title of the plot.
    """
    plt.figure(figsize=(8, 8))
    for path in paths:
        x_coords, y_coords = zip(*path)
        plt.plot(x_coords, y_coords, marker='o', markersize=2)  # Draw connected points
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    st.pyplot(plt)

def svg_to_coordinates(svg_file, resolution=100):
    paths, attributes = svg2paths(svg_file)
    coordinates = []
    for path in paths:
        for i in np.linspace(0, 1, resolution):
            point = path.point(i)
            coordinates.append((point.real, point.imag))
    return coordinates


def pipeline(jpeg_file, visualize=False):

    # Borders of the drawing
    min_x, max_x = 0, 300
    min_y, max_y = -150, 150

    # 1. Convert JPEG to SVG
    svg_file = jpg_to_svg(jpeg_file)

    # 2. Extract drawing paths from SVG
    paths = svg_to_paths(svg_file)

    # 3. Align with drawing borders of the robot
    adjusted_paths = adjust_points_to_borders(paths, min_x, max_x, min_y, max_y)

    # 4 Simplify paths
    simplified_paths = simplify_paths(adjusted_paths)

    #coordinates = []
    #for path in simplified_paths:
        #path_coords = []
        #for point in path:  # Assuming each path contains a list of points
            #x, y = point
            #path_coords.append((x, y))
        #coordinates.append(path_coords)

    # 5. Visualize paths (optional)
    if visualize:
        visualize_paths(simplified_paths)
        print(simplified_paths)
    
    return simplified_paths





