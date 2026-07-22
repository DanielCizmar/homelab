# TFT Display

## Purpose

Shows the current time and today's Slovak nameday on a TFT display.

## Hardware

The application is configured for a 128 x 128 pixel ST7735R SPI TFT, rotated 180 degrees. It uses the Raspberry Pi hardware SPI interface at 16 MHz.

## Pin connections

| Display pin | Raspberry Pi pin |
| --- | --- |
| VCC | 3.3 V (physical pin 1) |
| GND | Ground (physical pin 6) |
| SCK / SCL | GPIO 11 / SPI0 SCLK (physical pin 23) |
| MOSI / SDA | GPIO 10 / SPI0 MOSI (physical pin 19) |
| CS | GPIO 8 / SPI0 CE0 (physical pin 24) |
| DC / A0 | GPIO 25 (physical pin 22) |
| RST / RES | GPIO 24 (physical pin 18) |

The backlight is not controlled by the application; connect it according to the display module's requirements.

## Deployment

The display runs directly on the Raspberry Pi as the `homelab-display` systemd service. SPI must be enabled on the host. The service expects the repository at `/opt/homelab` and a Python virtual environment at `services/display/.venv`.

## Important files

- [`app/display.py`](app/display.py) — display configuration, drawing, and update loop.
- [`app/sk-meniny.json`](app/sk-meniny.json) — Slovak nameday data.
- [`systemd/homelab-display.service`](systemd/homelab-display.service) — systemd service definition.
- [`requirements.txt`](requirements.txt) — Python dependencies.

## Start

```sh
sudo systemctl enable --now homelab-display
sudo journalctl -u homelab-display -f
```
