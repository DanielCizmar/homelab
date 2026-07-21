#!/usr/bin/env python3

import json
import math
import signal
import time
from datetime import datetime
from pathlib import Path

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735


# ---------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------

WIDTH = 128
HEIGHT = 128
FPS = 10

APP_DIR = Path(__file__).resolve().parent
NAMEDAYS_FILE = APP_DIR / "sk-meniny.json"

REGULAR_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

running = True


# ---------------------------------------------------------------------
# Shutdown handling
# ---------------------------------------------------------------------

def stop_program(_signal_number, _frame):
    """
    Stop the main loop cleanly when Ctrl+C is pressed or when systemd
    stops the service.
    """
    global running
    running = False


signal.signal(signal.SIGTERM, stop_program)
signal.signal(signal.SIGINT, stop_program)


# ---------------------------------------------------------------------
# Namedays
# ---------------------------------------------------------------------

def load_namedays():
    """
    Load the Slovak nameday calendar.

    Expected JSON structure:

    {
        "7": {
            "19": "Dušana",
            "20": "Iľja, Eliáš"
        }
    }
    """
    try:
        with NAMEDAYS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("The top level of the JSON must be an object.")

        return data

    except FileNotFoundError:
        print(f"Nameday file not found: {NAMEDAYS_FILE}")

    except json.JSONDecodeError as error:
        print(f"Nameday JSON is invalid: {error}")

    except ValueError as error:
        print(f"Nameday data has an unexpected structure: {error}")

    return {}


def get_nameday(namedays, now):
    """
    Look up the nameday using month and day as string keys.

    Example:
        namedays["7"]["20"]
    """
    month = str(now.month)
    day = str(now.day)

    month_data = namedays.get(month)

    if not isinstance(month_data, dict):
        return "Neznáme"

    nameday = month_data.get(day, "Neznáme")

    if not isinstance(nameday, str):
        return "Neznáme"

    return nameday


# ---------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------

def draw_centered_text(draw, y, text, font, fill):
    """Draw text centered horizontally on the screen."""
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    x = max(0, (WIDTH - text_width) // 2)

    draw.text((x, y), text, font=font, fill=fill)


def fit_text(draw, text, font_path, maximum_width, starting_size):
    """
    Reduce the font size until the text fits within maximum_width.

    This is useful for namedays such as:
        Branislava, Bronislava
    """
    for font_size in range(starting_size, 7, -1):
        font = ImageFont.truetype(font_path, font_size)

        text_box = draw.textbbox((0, 0), text, font=font)
        text_width = text_box[2] - text_box[0]

        if text_width <= maximum_width:
            return font

    return ImageFont.truetype(font_path, 8)


def draw_fish(draw, x, y, direction=1):
    """Draw a small fish facing left or right."""
    body_width = 22
    body_height = 10

    if direction == 1:
        body_box = (
            x,
            y,
            x + body_width,
            y + body_height,
        )

        tail = [
            (x, y + body_height // 2),
            (x - 8, y - 3),
            (x - 8, y + body_height + 3),
        ]

        eye_x = x + 16

    else:
        body_box = (
            x - body_width,
            y,
            x,
            y + body_height,
        )

        tail = [
            (x, y + body_height // 2),
            (x + 8, y - 3),
            (x + 8, y + body_height + 3),
        ]

        eye_x = x - 16

    draw.ellipse(
        body_box,
        fill=(255, 165, 30),
        outline=(255, 230, 160),
    )

    draw.polygon(
        tail,
        fill=(255, 120, 20),
    )

    draw.ellipse(
        (
            eye_x - 1,
            y + 2,
            eye_x + 1,
            y + 4,
        ),
        fill=(0, 0, 0),
    )


# ---------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------

def main():
    namedays = load_namedays()

    # Display control pins.
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)

    # Hardware SPI interface.
    spi = board.SPI()

    display = st7735.ST7735R(
        spi,
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        width=WIDTH,
        height=HEIGHT,
        rotation=180,
        baudrate=16_000_000,
	x_offset=2,
	y_offset=3,
    )

    regular_font = ImageFont.truetype(REGULAR_FONT_PATH, 10)
    time_font = ImageFont.truetype(BOLD_FONT_PATH, 20)
    label_font = ImageFont.truetype(REGULAR_FONT_PATH, 9)

    fish_x = 15.0
    fish_direction = 1
    frame_number = 0

    while running:
        frame_started = time.monotonic()
        now = datetime.now()

        image = Image.new(
            "RGB",
            (WIDTH, HEIGHT),
            (3, 20, 35),
        )

        draw = ImageDraw.Draw(image)

        # Underwater section.
        draw.rectangle(
            (0, 82, WIDTH, HEIGHT),
            fill=(0, 55, 95),
        )

        # Animated waves.
        wave_offset = frame_number % 12

        for x in range(-12, WIDTH + 12, 12):
            draw.arc(
                (
                    x + wave_offset,
                    76,
                    x + wave_offset + 12,
                    88,
                ),
                0,
                180,
                fill=(60, 160, 210),
            )

        time_text = now.strftime("%H:%M:%S")
        date_text = now.strftime("%d.%m.%Y")
        nameday_text = get_nameday(namedays, now)

        draw_centered_text(
            draw,
            7,
            time_text,
            time_font,
            (255, 255, 255),
        )

        draw_centered_text(
            draw,
            31,
            date_text,
            regular_font,
            (180, 220, 255),
        )

        draw.text(
            (5, 49),
            "Meniny:",
            font=label_font,
            fill=(150, 190, 210),
        )

        nameday_font = fit_text(
            draw=draw,
            text=nameday_text,
            font_path=REGULAR_FONT_PATH,
            maximum_width=118,
            starting_size=11,
        )

        draw_centered_text(
            draw,
            62,
            nameday_text,
            nameday_font,
            (255, 220, 100),
        )

        # Fish moves up and down slightly while swimming.
        fish_y = 98 + int(math.sin(frame_number / 5) * 4)

        draw_fish(
            draw,
            int(fish_x),
            fish_y,
            fish_direction,
        )

        fish_x += 1.2 * fish_direction

        if fish_direction == 1 and fish_x > WIDTH - 25:
            fish_direction = -1

        elif fish_direction == -1 and fish_x < 25:
            fish_direction = 1

        display.image(image)

        frame_number += 1

        elapsed = time.monotonic() - frame_started
        remaining_time = (1 / FPS) - elapsed

        if remaining_time > 0:
            time.sleep(remaining_time)

    # Clear the display when the application stops cleanly.
    display.fill(0)


if __name__ == "__main__":
    main()
