from microbit import *
import spi

# Registers (command) for MAX7219
_NOOP = 0  # no-op (do nothing, doesn't change current status)
_DIGIT = [1, 2, 3, 4, 5, 6, 7, 8]  # digit (LED column)
_DECODEMODE = 9  # decode mode (1=on, 0-off; for 7-segment display on MAX7219, no usage here)
_INTENSITY = 10  # intensity (LED brightness level, 0-15)
_SCANLIMIT = 11  # scan limit (number of scanned digits)
_SHUTDOWN = 12  # turn on (1) or off (0)
_DISPLAYTEST = 15  # force all LEDs light up, no usage here

_pinCS = pin16  # LOAD pin, 0=ready to receive command, 1=command take effect
_matrixNum = 1  # number of MAX7219 matrix linked in the chain
_displayArray = []  # display array to show across all matrixes
_rotation = 0  # rotate matrix display for 4-in-1 modules
_reversed = False  # reverse matrix display order for 4-in-1 modules

def _registerAll(register, data):
    pin16.write_digital(0)
    for i in range(_matrixNum):
        spi.write(bytearray([register, data]))
    pin16.write_digital(1)

def clearAll():
    for i in range(8):
        _registerAll(_DIGIT[i], 0)

def setup(num, cs, mosi, miso, sck):
    global _pinCS, _matrixNum, _displayArray
    _pinCS = cs
    _matrixNum = num
    
    # prepare display array (for displaying texts; add extra 8 columns at each side as buffers)
    for i in range((num + 2) * 8):
        _displayArray.append(0)
    
    # set micro:bit SPI
    spi.init(baudrate=1000000, bits=8, mode=3, mosi=mosi, miso=miso, sck=sck)
    
    # initialize MAX7219s
    _registerAll(_SHUTDOWN, 0)  # turn off
    _registerAll(_DISPLAYTEST, 0)  # test mode off
    _registerAll(_DECODEMODE, 0)  # decode mode off
    _registerAll(_SCANLIMIT, 7)  # set scan limit to 7 (column 0-7)
    _registerAll(_INTENSITY, 15)  # set brightness to 15
    _registerAll(_SHUTDOWN, 1)  # turn on
    clearAll()  # clear screen on all MAX7219s

# Example of how to call the setup function
setup(1, pin16, pin15, pin14, pin13)
