import time
import board
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import neopixel
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

# datasheet: https://www.waveshare.com/wiki/RP2040-One
# cirquitpython firmware: https://circuitpython.org/board/raspberry_pi_pico/
# leds: https://github.com/raspberrypi/pico-micropython-examples/blob/master/blink/blink.py
# neopixel RGB LED: https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# buttons: https://learn.adafruit.com/multi-tasking-with-circuitpython/buttons
# debouncer: https://docs.circuitpython.org/projects/debouncer/en/latest/api.html#adafruit-debouncer

# configs (GRB)
GREEN = (255, 0, 0)
RED = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (80, 220, 20)
PURPLE = (20, 185, 200)
WHITE = ( 255, 255, 255 )
COLORS = [ WHITE, GREEN, BLUE ]
COLORS_DISABLED = [ RED ]
MOUSE_INTERVAL = 60

# runtime variables
switchstates = {}
switchl = None
switchr = None
mouse = None
keyboard = None
keyboardlayout = None
pixels = None
time_mouse = -1 - MOUSE_INTERVAL
mouse_offset_y = 5
mouse_enabled = False
led_ctr = len(COLORS)

def staticpin(pin, value=True):
    """ Initialize a pin with a static output value """
    pin = DigitalInOut(pin)
    pin.direction = Direction.OUTPUT
    pin.value = value
    return pin

def pinswitch(pin):
    """ Create a switch """
    btn = DigitalInOut(pin)
    btn.direction = Direction.INPUT
    btn.pull = Pull.DOWN
    switch = Debouncer(btn)

    if pin not in switchstates:
        switchstates[pin] = False

    return (pin, switch)

def pinpressed(pin):
    """ Check if a pin switch was pressed """
    global switchstates
    pin[1].update()
    pressed = switchstates[pin[0]] != pin[1].value and pin[1].value == True
    switchstates[pin[0]] = pin[1].value
    return pressed

def mousemove():
    """ Move the mouse once """
    global mouse_offset_y
    mouse.move(0, mouse_offset_y)
    mouse_offset_y = mouse_offset_y * -1

def init():
    """ Init hardware and variables """
    global switchl
    global switchr
    global mouse
    global keyboard
    global keyboardlayout
    global pixels

    staticpin(board.GP11, True)
    switchl = pinswitch(board.GP13)
    switchr = pinswitch(board.GP9)

    mouse = Mouse(usb_hid.devices)
    keyboard = Keyboard(usb_hid.devices)
    keyboardlayout = KeyboardLayoutUS(keyboard)
    pixels = neopixel.NeoPixel(board.GP16, 1, brightness=0.03, auto_write=False)

def tick():
    """ Main function """

    # current time
    now = time.monotonic()

    # enable/disable button
    global mouse_enabled
    global time_mouse
    if pinpressed(switchl):
        mouse_enabled = not mouse_enabled
        time_mouse = -1 - MOUSE_INTERVAL
        print("Mouse jiggler enabled" if mouse_enabled else "Mouse jiggler disabled")

    if pinpressed(switchr):
        keyboard.send(Keycode.CONTROL, Keycode.A)
        keyboardlayout.write('Hello  World', delay=0.01)

    # change led and move mouse
    global led_ctr
    if now - time_mouse > MOUSE_INTERVAL:
        usedcolors = COLORS
        if mouse_enabled:
            mousemove()
        else:
            usedcolors = COLORS_DISABLED

        pixels.fill(usedcolors[ led_ctr % len(usedcolors) ])
        if led_ctr > len(usedcolors):
            led_ctr = 1
        pixels.show()

        time_mouse = now
        led_ctr += 1

# main loop
init()
while True:
    tick()
    time.sleep(0.01)
