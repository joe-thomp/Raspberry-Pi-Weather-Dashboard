#!/usr/bin/env python3
"""
Download weather icons from InkyPi repository
"""

import urllib.request
import os

# Base URL for the icons
base_url = "https://raw.githubusercontent.com/fatihak/InkyPi/main/src/plugins/weather/icons/"

# List of all icon files to download
icon_files = [
    # Weather condition icons
    "01d.png", "02d.png", "03d.png", "04d.png",
    "09d.png", "10d.png", "11d.png", "13d.png", "50d.png",

    # Metric icons
    "humidity.png", "pressure.png", "visibility.png",
    "wind.png", "aqi.png", "uvi.png",

    # Astronomical icons
    "sunrise.png", "sunset.png",
    "newmoon.png", "firstquarter.png", "fullmoon.png", "lastquarter.png",
    "waxingcrescent.png", "waxinggibbous.png", "waningcrescent.png", "waninggibbous.png"
]

# Create icons directory if it doesn't exist
icons_dir = "icons"
os.makedirs(icons_dir, exist_ok=True)

print("Downloading weather icons from InkyPi repository...")
print("=" * 50)

downloaded = 0
failed = 0

for icon_file in icon_files:
    try:
        url = base_url + icon_file
        filepath = os.path.join(icons_dir, icon_file)

        print(f"Downloading {icon_file}...", end=" ")
        urllib.request.urlretrieve(url, filepath)
        print("OK")
        downloaded += 1
    except Exception as e:
        print(f"FAILED ({e})")
        failed += 1

print("\n" + "=" * 50)
print(f"Downloaded: {downloaded} icons")
if failed > 0:
    print(f"Failed: {failed} icons")
print(f"Icons saved to: {os.path.abspath(icons_dir)}")
