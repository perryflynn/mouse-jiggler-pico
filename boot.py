import board
import storage
import usb_cdc
import usb_midi
from digitalio import DigitalInOut, Direction, Pull

# set input for switches to high
src = DigitalInOut(board.GP11)
src.direction = Direction.OUTPUT
src.value = True

# read left switch value
btn = DigitalInOut(board.GP13)
btn.direction = Direction.INPUT
btn.pull = Pull.DOWN

if not btn.value:
    print("Left switch was not pressed on boot, disable usb flash drive and repl!")
    storage.disable_usb_drive()
    usb_cdc.disable()
    usb_midi.disable()
