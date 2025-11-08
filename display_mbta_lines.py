#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import os

def create_colors_arr ( lines ):
    colors = []
    for line in lines:
        print(line)
        tmp_route_id = line.get('route_id').lower()
        if "green" in tmp_route_id:
            colors.append( graphics.Color(0, 0, 255) )
        elif "red" in tmp_route_id:
            colors.append( graphics.Color(255, 0, 0) )
        else:
            graphics.Color(0, 255, 0)

    return colors

def display_lines( lines, font_path="MBTA-app/rpi-rgb-led-matrix/fonts/4x6.bdf" ):

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
    home_dir = os.path.expanduser("~")
    font_path = os.path.join(home_dir, font_path)
    font.LoadFont(font_path)  # adjust path

    # Text colors
    colors = create_colors_arr( lines )

    # Starting y positions
    start_y = 6
    line_spacing = 8

    # Initialize x positions for scrolling (start at right edge)
    x_pos = canvas.width

    scroll_speed = 0.2  # pixels per frame (lower = slower)
    frame_delay = 0.03   # seconds between frames

    try:
        while True:
            canvas.Clear()
            for i, line_dict in enumerate(lines):
                # Draw text at current x position
                graphics.DrawText(canvas, font, x_pos, start_y + i * line_spacing, colors[i % len(colors)], line_dict['text'])
                
                # Update x position for scrolling left
                x_pos -= scroll_speed
                
                # Reset to right side when completely off-screen
                text_width = graphics.DrawText(canvas, font, 0, 0, colors[i], line_dict['text'])  # width in pixels
                if x_pos < -text_width:
                    x_pos = canvas.width

            canvas = matrix.SwapOnVSync(canvas)
            time.sleep(frame_delay)

    except KeyboardInterrupt:
        print("\nExiting and clearing display.")
        matrix.Clear()
