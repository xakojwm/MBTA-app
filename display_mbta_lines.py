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

def display_lines(lines, font_path="MBTA-app/rpi-rgb-led-matrix/fonts/4x6.bdf"):
    # --- Configuration ---
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'

    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    # --- Load font ---
    font = graphics.Font()
    home_dir = os.path.expanduser("~")
    font_path = os.path.join(home_dir, font_path)
    font.LoadFont(font_path)

    # --- Colors ---
    colors = create_colors_arr(lines)
    divider_color = graphics.Color(60, 60, 60)  # dim gray lines

    # --- Layout settings ---
    num_rows = len(lines)
    row_height = options.rows // num_rows       # equally divide display
    col_divider_x = 20                          # position of vertical divider
    col1_x = 1                                  # static text x start
    col2_start_x = col_divider_x + 3            # moving text starts after divider

    scroll_speed = 0.4
    frame_delay = 0.03

    # Shared scroll offset for all rows
    col2_x = options.cols

    try:
        while True:
            canvas.Clear()

            # --- Draw table dividers ---
            graphics.DrawLine(canvas, col_divider_x, 0, col_divider_x, options.rows - 1, divider_color)
            for i in range(1, num_rows):
                y_line = i * row_height
                graphics.DrawLine(canvas, 0, y_line, options.cols - 1, y_line, divider_color)

            # --- Draw each row ---
            for i, line_dict in enumerate(lines):
                color = colors[i % len(colors)]
                y_center = (i * row_height) + row_height // 2 + 2

                # Static column (left side)
                graphics.DrawText(canvas, font, col1_x, y_center, color, line_dict['static_text'])

                # Scrolling column (right side)
                scroll_x = int(col2_x)
                moving_text = line_dict['moving_text']
                text_width = graphics.DrawText(canvas, font, 0, 0, color, moving_text)

                if scroll_x + text_width > col2_start_x:
                    if scroll_x >= col2_start_x:
                        graphics.DrawText(canvas, font, scroll_x, y_center, color, moving_text)
                    else:
                        # Clip portion hidden by divider
                        overlap = col2_start_x - scroll_x
                        avg_char_width = 6
                        skip_chars = min(len(moving_text), int(overlap / avg_char_width))
                        visible_text = moving_text[skip_chars:]
                        if visible_text:
                            graphics.DrawText(canvas, font, col2_start_x, y_center, color, visible_text)

            # --- Update scroll position ---
            col2_x -= scroll_speed
            if col2_x < -options.cols:
                col2_x = options.cols

            canvas = matrix.SwapOnVSync(canvas)
            time.sleep(frame_delay)

    except KeyboardInterrupt:
        print("\nExiting and clearing display.")
        matrix.Clear()