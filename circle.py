import math
from lib.dobot import Dobot

def draw_circle(bot, center=None, radius=50, steps=24):
    """
    Draw a circle using the Dobot robot.
    
    Args:
        bot: Dobot object for the robot
        center: Center position [x, y, z, r] (if None, uses current position)
        radius: Radius of the circle in mm (default: 50)
        steps: Number of points to draw the circle (default: 24)
        
    Returns:
        bool: True if circle was drawn successfully
    """
    try:
        # Get center position if not provided
        if center is None:
            print('Getting current position as center...')
            center = bot.get_pose()
            print('Center:', center)
        
        # Lift pen up
        print('Lifting pen...')
        bot.move_to_relative(0, 0, 10, 0)
        print('Ready to draw')
        
        # Lower pen down
        bot.move_to_relative(0, 0, -10, 0)
        
        # Set trajectory parameters for smooth drawing
        bot.interface.set_continous_trajectory_params(200, 200, 200)
        
        # Generate circle path
        path = []
        for i in range(steps + 2):
            angle = ((math.pi * 2) / steps) * i
            x = math.cos(angle)
            y = math.sin(angle)
            path.append([center[0] + x * radius, center[1] + y * radius, center[2]])
        
        # Draw the circle
        print(f'Drawing circle with radius {radius}mm...')
        bot.follow_path(path)
        
        # Lift pen and return to center
        print('Lifting pen and returning to start...')
        bot.move_to_relative(0, 0, 10, 0)
        bot.slide_to(center[4], center[5], center[6], center[7])
        
        print('Circle drawn successfully!')
        return True
        
    except Exception as e:
        print(f'Error drawing circle: {e}')
        return False


# Usage example
if __name__ == "__main__":
    bot = Dobot('/dev/tty.usbserial-0001')
    
    print('Homing')
    # bot.home()
    
    print('Unlock the arm and place it on the middle of the paper')
    input("Press enter to continue...")
    
    # Draw circle at current position
    draw_circle(bot, radius=50, steps=24)
    