import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from lib.interface import Interface



bot = Interface('/dev/tty.usbserial-0001')
print('Bot status:', 'connected' if bot.connected() else 'not connected')

params = bot.get_homing_paramaters()
print('Params:', params)



def move_to_home(bot):
    """
    Move the bot to its home position.
    
    Args:
        bot: Interface object for the bot
        
    Returns:
        bool: True if homing command was sent successfully, False otherwise
    """
    if not bot.connected():
        raise ConnectionError("Bot is not connected")
    
    print("Moving to home position...")
    bot.set_homing_command(0)
    print("Homing command sent")
    return True
# Use the function
move_to_home(bot)