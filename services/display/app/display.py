#!/usr/bin/env python3

import json
import signal
import time
from datetime import datetime
from pathlib import Path

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735


# ---------------------------------------------------------------------
# Display configuration
# ---------------------------------------------------------------------

WIDTH = 128
HEIGHT = 128

ROTATION = 180
X_OFFSET = 2
Y_OFFSET = 3

APP_DIR = Path(__file__).resolve().parent
NAMEDAYS_FILE = APP_DIR / "sk-meniny.json"

REGULAR_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Night-friendly colors.
#
# Values range from 0 to 255:
# (red, green, blue)
BACKGROUND_COLOR = (0, 0, 0)
HOUR_COLOR = (130, 25, 10)
MINUTE_COLOR = (160, 35, 12)
SECOND_COLOR = (100, 18, 8)
DIVIDER_COLOR = (45, 10, 5)
LABEL_COLOR = (75, 22, 12)
NAMEDAY_COLOR = (115, 32, 14)

running = True


# ---------------------------------------------------------------------
# Shutdown handling
# ---------------------------------------------------------------------

def stop_program(_signal_number, _frame):
    """Tell the main loop to stop cleanly."""
    global running
    running = False


signal.signal(signal.SIGTERM, stop_program)
signal.signal(signal.SIGINT, stop_program)


# ---------------------------------------------------------------------
# Font handling
# ---------------------------------------------------------------------

def load_font(path, size):
    """
    Load a TrueType font.

    If the requested font is missing, use Pillow's built-in font so the
    application does not crash.
    """
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        print(f"Warning: could not load font: {path}")
        return ImageFont.load_default()


def fit_font(draw, text, font_path, maximum_width, starting_size):
    """Reduce the font size until the text fits the available width."""
    for size in range(starting_size, 7, -1):
        font = load_font(font_path, size)
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0]

        if width <= maximum_width:
            return font

    return load_font(font_path, 8)


# ---------------------------------------------------------------------
# Nameday handling
# ---------------------------------------------------------------------

def load_namedays():
    """
    Load namedays from this structure:

    {
        "7": {
            "20": "Iľja, Eliáš"
        }
    }
    """
    try:
        with NAMEDAYS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("The top level of the nameday JSON must be an object.")

        return data

    except FileNotFoundError:
        print(f"Nameday file not found: {NAMEDAYS_FILE}")

    except json.JSONDecodeError as error:
        print(f"Invalid nameday JSON: {error}")

    except ValueError as error:
        print(f"Unexpected nameday structure: {error}")

    return {}


def get_nameday(namedays, now):
    """Return today's nameday using month and day string keys."""
    month = str(now.month)
    day = str(now.day)

    month_data = namedays.get(month, {})

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
    """Draw text centered horizontally."""
    box = draw.textbbox((0, 0), text, font=font)

    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    x = (WIDTH - text_width) // 2

    # Subtract box[1] because some fonts have a vertical top offset.
    draw.text(
        (x, y - box[1]),
        text,
        font=font,
        fill=fill,
    )

    return text_height


def draw_screen(display, namedays, now, time_font, label_font):
    """Create and send one complete screen image."""
    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND_COLOR,
    )

    draw = ImageDraw.Draw(image)

    hour_text = now.strftime("%H")
    minute_text = now.strftime("%M")
    second_text = now.strftime("%S")
    nameday_text = get_nameday(namedays, now)

    # Three large clock lines.
    draw_centered_text(
        draw,
        1,
        hour_text,
        time_font,
        HOUR_COLOR,
    )

    draw_centered_text(
        draw,
        32,
        minute_text,
        time_font,
        MINUTE_COLOR,
    )

    draw_centered_text(
        draw,
        63,
        second_text,
        time_font,
        SECOND_COLOR,
    )

    # Separator between the clock and the nameday.
    draw.line(
        (10, 94, 117, 94),
        fill=DIVIDER_COLOR,
        width=1,
    )

    draw_centered_text(
        draw,
        98,
        "Meniny",
        label_font,
        LABEL_COLOR,
    )

    # Long namedays automatically use a smaller font.
    nameday_font = fit_font(
        draw=draw,
        text=nameday_text,
        font_path=REGULAR_FONT_PATH,
        maximum_width=122,
        starting_size=11,
    )

    draw_centered_text(
        draw,
        113,
        nameday_text,
        nameday_font,
        NAMEDAY_COLOR,
    )

    display.image(image)


# ---------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------

def main():
    namedays = load_namedays()

    # TFT control pins.
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)

    # Raspberry Pi hardware SPI interface.
    spi = board.SPI()

    display = st7735.ST7735R(
        spi,
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        width=WIDTH,
        height=HEIGHT,
        rotation=ROTATION,
        x_offset=X_OFFSET,
        y_offset=Y_OFFSET,
        baudrate=16_000_000,
    )

    time_font = load_font(BOLD_FONT_PATH, 31)
    label_font = load_font(REGULAR_FONT_PATH, 9)

    previous_second = None

    while running:
        now = datetime.now()

        # Only redraw when the second changes.
        if now.second != previous_second:
            draw_screen(
                display=display,
                namedays=namedays,
                now=now,
                time_font=time_font,
                label_font=label_font,
            )

            previous_second = now.second

        # Prevent unnecessary CPU usage while waiting for the next second.
        time.sleep(0.05)

    # Clear pixels when the service stops cleanly.
    display.fill(0)


if __name__ == "__main__":
    main()