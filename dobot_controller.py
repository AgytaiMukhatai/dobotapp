from pydobot import Dobot


class DobotController:
    def __init__(self, port):
        """Initialize the DobotController and set speed."""
        try:
            self.bot = Dobot(port=port, verbose=False)
            self.bot.speed(100, 100)
        except AttributeError as e:
            print(f"Error initializing Dobot: {e}")
            raise

    def set_home_position(self, x, y, z):
        """
        Set the home position for the Dobot.

        This function moves the Dobot to the specified position (x, y, z), 
        sets the current position as the new home position, 
        and then tests the new home position to ensure it is correctly set.

        Parameters:
            x (float): The x-coordinate of the new home position.
            y (float): The y-coordinate of the new home position.
            z (float): The z-coordinate of the new home position.

        Returns:
        None
        """
        self.bot.move_to(x, y, z, 0, wait=True)
        self.bot.set_home_command()
        self.bot.home()

    def move_pen(self, x, y, z):
        """Move the pen/tool to specified coordinates."""
        try:
            self.bot.move_to(x, y, z, 0, wait=True)
        except Exception as e:
            print(f"Error moving to point ({x}, {y}, {z}): {e}")

    def validate_point(self, point):
        """Ensure a point contains float coordinates."""
        if len(point) != 2:
            raise ValueError(f"Invalid point: {point}. Must have two coordinates.")
        return float(point[0]), float(point[1])

    def draw_path(self, path, draw_z=-60, lift_z=-50):
        """Draw a path connecting all points in the given path."""
        if len(path) < 2:
            print("Path is too short to draw.")
            return

        for i, point in enumerate(path):
            x, y = self.validate_point(point)
            print(f"Drawing point {i + 1}: ({x}, {y})")  # Added print to show the drawing step
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


