#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# --- Configuration ---
options = RGBMatrixOptions()
options.rows = 32           # Change based on your LED panel
options.cols = 64           # Change based on your LED panel
options.chain_length = 1    # Number of chained panels
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # Use 'adafruit-hat' or 'regular' as needed

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# Load font
font = graphics.Font()
font.LoadFont("/home/wyattmorris/rpi-rgb-led-matrix/fonts/4x6.bdf")

# Define text colors
colors = [
    graphics.Color(255, 0, 0),     # Red
    graphics.Color(0, 255, 0),     # Green
    graphics.Color(0, 0, 255),     # Blue
    graphics.Color(255, 255, 0)    # Yellow
]

# Define text lines (you can change these)
lines = [
    "Line 1: Hello, World!",
    "Line 2: Raspberry Pi",
    "Line 3: LED Matrix",
    "Line 4: 4 Rows of Text"
]

# Y positions for each line
start_y = 10  # Starting y position
line_spacing = 8  # Space between lines

try:
    while True:
        canvas.Clear()
        for i, text in enumerate(lines):
            y = start_y + i * line_spacing
            graphics.DrawText(canvas, font, 2, y, colors[i % len(colors)], text)
        canvas = matrix.SwapOnVSync(canvas)
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nExiting and clearing display.")
    matrix.Clear()

