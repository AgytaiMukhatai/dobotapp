import matplotlib.pyplot as plt
from PIL import Image
import svgpathtools
import os
import subprocess
import matplotlib.animation as animation

# Function to convert JPEG to SVG using potrace
def jpeg_to_svg(jpeg_file):
    """
    Converts a JPEG image to an SVG file using potrace.

    Parameters:
    - jpeg_file (str): Path to the JPEG file.

    Returns:
    - svg_file (str): Path to the generated SVG file.
    """
    # Convert JPEG to PNM format (required by potrace)
    
    pnm_file = jpeg_file.replace('.jpeg', '.pnm')
    svg_file = jpeg_file.replace('.jpeg', '.svg')
    
    
    Image.open(jpeg_file).convert('L').save(pnm_file)

    # Use potrace to convert PNM to SVG
    subprocess.run(["potrace", "-s", pnm_file, "-o", svg_file])

    # Clean up the intermediate PNM file
    os.remove(pnm_file)

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
    plt.show()


def pipeline(jpeg_file, visualize=False):

    # Borders of the drawing
    min_x, max_x = 230, 250
    min_y, max_y = -10, 10

    # 1. Convert JPEG to SVG
    svg_file = jpeg_to_svg(jpeg_file)