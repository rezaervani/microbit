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
# setup(1, pin16, pin15, pin14, pin13)

# Rotation/reverse order options for 4-in-1 MAX7219 modules
def for_4_in_1_modules(rotation, reversed):
    global _rotation, _reversed
    _rotation = rotation
    _reversed = reversed

# (internal function) write command and data to all MAX7219s
def _registerAll(addressCode, data):
    _pinCS.write_digital(0)  # LOAD=LOW, start to receive commands
    for i in range(_matrixNum):
        # when a MAX7219 received a new command/data set
        # the previous one would be pushed to the next matrix along the chain via DOUT
        spi.write(bytearray([addressCode]))  # command (8 bits)
        spi.write(bytearray([data]))  # data (8 bits)
    _pinCS.write_digital(1)  # LOAD=HIGH, commands take effect

# (internal function) write command and data to a specific MAX7219 (index 0=farthest on the chain)
def _registerForOne(addressCode, data, matrixIndex):
    if matrixIndex <= _matrixNum - 1:
        _pinCS.write_digital(0)  # LOAD=LOW, start to receive commands
        for i in range(_matrixNum):
            # when a MAX7219 received a new command/data set
            # the previous one would be pushed to the next matrix along the chain via DOUT
            if i == matrixIndex:  # send change to target
                spi.write(bytearray([addressCode]))  # command (8 bits)
                spi.write(bytearray([data]))  # data (8 bits)
            else:  # do nothing to non-targets
                spi.write(bytearray([_NOOP]))
                spi.write(bytearray([0]))
        _pinCS.write_digital(1)  # LOAD=HIGH, commands take effect

# Example usage of for_4_in_1_modules
# for_4_in_1_modules(0, False)  # rotation_direction.none is assumed to be 0 in this example

# (internal function) rotate matrix
def _rotateMatrix(matrix):
    global _rotation
    tmp = 0
    for i in range(4):
        for j in range(i, 7 - i):
            tmp = matrix[i][j]
            if _rotation == 1:  # assuming 1 represents clockwise rotation
                # clockwise
                matrix[i][j] = matrix[j][7 - i]
                matrix[j][7 - i] = matrix[7 - i][7 - j]
                matrix[7 - i][7 - j] = matrix[7 - j][i]
                matrix[7 - j][i] = tmp
            elif _rotation == 2:  # assuming 2 represents counterclockwise rotation
                # counter-clockwise
                matrix[i][j] = matrix[7 - j][i]
                matrix[7 - j][i] = matrix[7 - i][7 - j]
                matrix[7 - i][7 - j] = matrix[j][7 - i]
                matrix[j][7 - i] = tmp
            elif _rotation == 3:  # assuming 3 represents 180 degree rotation
                # 180 degree
                matrix[i][j] = matrix[7 - i][7 - j]
                matrix[7 - i][7 - j] = tmp
                tmp = matrix[7 - j][i]
                matrix[7 - j][i] = matrix[j][7 - i]
                matrix[j][7 - i] = tmp
    return matrix

# Example usage of _rotateMatrix
# matrix = [
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0]
# ]

# _rotation = 1  # Set to desired rotation direction
# matrix = _rotateMatrix(matrix)

# (internal function) get 8x8 matrix from a column array
def _getMatrixFromColumns(columns):
    matrix = [[0 for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(7, -1, -1):
            if columns[i] >= 2 ** j:
                columns[i] -= 2 ** j
                matrix[i][j] = 1
            elif columns[i] == 0:
                break
    return matrix

# Example usage of _getMatrixFromColumns
# columns = [0, 0, 0, 0, 0, 0, 0, 0]
# matrix = _getMatrixFromColumns(columns)

# from microbit import sleep

# Scroll a text across all MAX7219 matrices for once
def scrollText(text, delay, endDelay):
    global _displayArray
    printPosition = len(_displayArray) - 8
    characters_index = []
    currentChrIndex = 0
    currentFontArray = []
    nextChrCountdown = 1
    chrCountdown = []
    totalScrollTime = 0

    # Clear screen and array
    for i in range(len(_displayArray)):
        _displayArray[i] = 0
    clearAll()

    # Get font index of every character and total scroll time needed
    for i in range(len(text)):
        index = font.index(text[i]) if text[i] in font else -1
        if index >= 0:
            characters_index.append(index)
            chrCountdown.append(len(font_matrix[index]))
            totalScrollTime += len(font_matrix[index])

    totalScrollTime += _matrixNum * 8

    # Print characters into array and scroll the array
    for i in range(totalScrollTime):
        nextChrCountdown -= 1
        if currentChrIndex < len(characters_index) and nextChrCountdown == 0:
            # Print a character just "outside" visible area
            currentFontArray = font_matrix[characters_index[currentChrIndex]]
            if currentFontArray is not None:
                for j in range(len(currentFontArray)):
                    _displayArray[printPosition + j] = currentFontArray[j]
            # Wait until current character scrolled into visible area
            nextChrCountdown = chrCountdown[currentChrIndex]
            currentChrIndex += 1
        
        # Scroll array (copy all columns to the one before it)
        for j in range(len(_displayArray) - 1):
            _displayArray[j] = _displayArray[j + 1]
        _displayArray[len(_displayArray) - 1] = 0

        # Write every 8 columns of display array (visible area) to each MAX7219s
        matrixCountdown = _matrixNum - 1
        for j in range(8, len(_displayArray) - 8, 8):
            if matrixCountdown < 0:
                break
            actualMatrixIndex = matrixCountdown if not _reversed else _matrixNum - 1 - matrixCountdown
            if _rotation == 0:  # assuming 0 represents no rotation
                for k in range(j, j + 8):
                    _registerForOne(_DIGIT[k - j], _displayArray[k], actualMatrixIndex)
            else:  # Rotate matrix if needed
                tmpColumns = [0] * 8
                for k in range(j, j + 8):
                    tmpColumns[k - j] = _displayArray[k]
                displayLEDsForOne(_getMatrixFromColumns(tmpColumns), actualMatrixIndex)
            matrixCountdown -= 1
        sleep(delay)
    sleep(endDelay)

# Example usage of scrollText
# font = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Example font
# font_matrix = [
#     [0x7e, 0x81, 0x81, 0x81, 0x7e],  # Example character matrices
#     [0x00, 0x00, 0x00, 0x00, 0x00],  # Add more as needed
#     # ...
# ]

# _displayArray = [0] * 24  # Example display array size
# _matrixNum = 3  # Example number of matrices
# _rotation = 0  # No rotation
# _reversed = False  # No reverse

# scrollText("HELLO", 75, 500)

