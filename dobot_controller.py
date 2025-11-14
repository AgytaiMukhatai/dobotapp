from pydobot import Dobot


class DobotController:
    def __init__(self, port):
        """Initialize the DobotController and set speed."""
        try:
            self.bot = Dobot(port=port, verbose=False)
            self.bot.speed(1200, 1200)
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

    def draw_path(self, path, draw_z=-51.4, lift_z=-20):
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
    
    def emergency_stop(self):
        """Best-effort software emergency stop."""
        try:
            # If pydobot exposes a clear/stop method, call it here.
            # Fallback: just print for now so it doesn't crash.
            print("Emergency stop requested – implement hardware stop here if available.")
        except Exception as e:
            print(f"Error during emergency stop: {e}")

    def draw_paths(self, coordinates, stop_event=None, draw_z=-51.4, lift_z=-20):
        """
        Draw multiple paths with optional cooperative emergency stop.

        coordinates: iterable of paths, where each path is iterable of (x, y) points.
        """
        for path_idx, path in enumerate(coordinates):
            if stop_event is not None and stop_event.is_set():
                print("Stop event set before starting path, stopping.")
                self.emergency_stop()
                break

            if not path:
                continue

            print(f"Starting path {path_idx + 1} with {len(path)} points")

            for i, point in enumerate(path):
                if stop_event is not None and stop_event.is_set():
                    print("Stop event set during path, stopping.")
                    self.emergency_stop()
                    break

                x, y = self.validate_point(point)

                if i == 0:
                    # Move above first point, then down to drawing height
                    self.move_pen(x, y, lift_z)
                    self.move_pen(x, y, draw_z)
                else:
                    # Draw to next point
                    self.move_pen(x, y, draw_z)

            # After finishing this path, lift the pen
            last_x, last_y = self.validate_point(path[-1])
            self.move_pen(last_x, last_y, lift_z)

            if stop_event is not None and stop_event.is_set():
                # Already handled emergency_stop inside loop, just break out of paths loop
                break
        print("Finished drawing all paths.")



