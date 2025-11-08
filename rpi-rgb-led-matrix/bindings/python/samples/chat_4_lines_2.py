#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# --- Configuration ---
options = RGBMatrixOptions()
options.rows = 32           # Change based on your panel
options.cols = 64           # Change based on your panel
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()

# Load font (use a valid .bdf font path)
font = graphics.Font()
font.LoadFont("/home/wyattmorris/rpi-rgb-led-matrix/fonts/6x10.bdf")  # adjust path

# Text colors
colors = [
    graphics.Color(255, 0, 0),
    graphics.Color(0, 255, 0),
    graphics.Color(0, 0, 255),
    graphics.Color(255, 255, 0)
]

# Lines to scroll
lines = [
    "Line 1: Hello, World!",
    "Line 2: Raspberry Pi",
    "Line 3: LED Matrix",
    "Line 4: 4 Rows of Text"
]

# Starting y positions
start_y = 10
line_spacing = 8

# Initialize x positions for scrolling (start at right edge)
x_positions = [canvas.width for _ in lines]

scroll_speed = 1  # pixels per frame

try:
    while True:
        canvas.Clear()
        for i, text in enumerate(lines):
            # Draw text at current x position
            graphics.DrawText(canvas, font, x_positions[i], start_y + i * line_spacing, colors[i % len(colors)], text)
            
            # Update x position for scrolling left
            x_positions[i] -= scroll_speed
            
            # Reset to right side when completely off-screen
            text_width = graphics.DrawText(canvas, font, 0, 0, colors[i], text)  # width in pixels
            if x_positions[i] < -text_width:
                x_positions[i] = canvas.width

        canvas = matrix.SwapOnVSync(canvas)
        time.sleep(0.03)

except KeyboardInterrupt:
    print("\nExiting and clearing display.")
    matrix.Clear()
