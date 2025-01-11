from pydobot import Dobot

class DobotController:
    def __init__(self, port):
        """Initialize the DobotController and set speed."""
        self.bot = Dobot(port=port, verbose=False)
        self.bot.speed(100, 100)
    
    def set_home_position(self, x, y, z):
        self.bot.move_to(x, y, z, 0, wait=True) 

        # Set the current position as the new home position
        self.bot.set_home_command()  # This command saves the current position as the home

        # Test the new home position
        self.bot.home()  #

    def move_pen(self, x, y, z):
        """Move the pen/tool to specified coordinates."""
        self.bot.move_to(x, y, z, 0, wait=True)

    def validate_point(self, point):
        """Ensure a point contains float coordinates."""
        if len(point) != 2:
            raise ValueError(f"Invalid point: {point}. Must have two coordinates.")
        return float(point[0]), float(point[1])

    def draw_line(self, x1, y1, x2, y2, z=-60):
        """Draw a line from (x1, y1) to (x2, y2) at a specified Z level."""
        self.move_pen(x1, y1, z)
        self.move_pen(x2, y2, z)

    def draw_path(self, path, draw_z=-60, lift_z=-50):
        """Draw a path connecting all points in the given path."""
        if len(path) < 2:
            print("Path is too short to draw.")
            return

        for i, point in enumerate(path):
            x, y = self.validate_point(point)
            if i == 0:
                self.move_pen(x, y, lift_z)  # Start at lift height
                self.move_pen(x, y, draw_z)  # Lower pen to start drawing
            else:
                self.move_pen(x, y, draw_z)  # Draw to next point

        # Lift the pen after completing the path
        x, y = self.validate_point(path[-1])
        self.move_pen(x, y, lift_z)

    def draw_paths(self, paths, draw_z=-60, lift_z=-30):
        """Draw multiple paths, lifting the pen between paths."""
        for path in paths:
            if path:
                self.draw_path(path, draw_z, lift_z)
            else:
                print("Skipping empty path.")
        print("Finished drawing all paths.")