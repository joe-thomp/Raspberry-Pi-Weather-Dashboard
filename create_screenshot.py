#!/usr/bin/env python3
"""
Generate a screenshot for the README without needing Raspberry Pi hardware.
This creates the exact same image that would display on the Inky Impression.
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime, timedelta
import os

# Display dimensions
WIDTH = 800
HEIGHT = 480

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (5, 8, 15)
TEXT_SECONDARY = (200, 200, 220)
ORANGE = (255, 140, 66)
BLUE = (100, 150, 255)


def load_font(size, bold=False):
    """Load font with fallbacks"""
    paths = [
        'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()


def load_icon(name, size):
    """Load icon from icons folder"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, 'icons', f'{name}.png')
    if os.path.exists(icon_path):
        try:
            icon = Image.open(icon_path).convert('RGBA')
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)
            icon = ImageEnhance.Sharpness(icon).enhance(1.5)
            icon = ImageEnhance.Color(icon).enhance(1.8)
            icon = ImageEnhance.Contrast(icon).enhance(1.5)
            return icon
        except:
            pass
    return Image.new('RGBA', (size, size), (0, 0, 0, 0))


def bezier_curve(points, segments=20):
    """Smooth curve interpolation"""
    if len(points) < 2:
        return points
    result = []
    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]
        for t_step in range(segments):
            t = t_step / segments
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                      (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                      (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                      (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                      (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            result.append((int(x), int(y)))
    result.append(points[-1])
    return result


def create_screenshot():
    print("Creating screenshot...")

    # Load fonts
    fonts = {
        'location': load_font(30, bold=True),
        'date': load_font(17),
        'temp_large': load_font(90),
        'temp_unit': load_font(42),
        'description': load_font(17),
        'feels': load_font(16),
        'detail_label': load_font(13),
        'detail_value': load_font(18, bold=True),
        'axis': load_font(11),
        'forecast_day': load_font(16, bold=True),
        'forecast_temp': load_font(13),
    }

    # Sample data - Philadelphia with rain chances
    now = datetime.now()
    data = {
        'city': 'Philadelphia',
        'state': 'PA',
        'date': now.strftime('%A, %B %d'),
        'time': now.strftime('%I:%M%p').lstrip('0').lower(),
        'temp': 54,
        'feels': 51,
        'desc': 'Partly Cloudy',
        'humidity': 60,
        'wind': 5.99,
        'visibility': 10.0,
        'uv': 2.9,
        'aqi': 2,
        'sunrise': '7:20 AM',
        'sunset': '5:10 PM',
        'hourly': [
            {'temp': 54, 'rain': 5},
            {'temp': 52, 'rain': 10},
            {'temp': 48, 'rain': 15},
            {'temp': 45, 'rain': 25},
            {'temp': 43, 'rain': 35},
            {'temp': 42, 'rain': 40},
            {'temp': 41, 'rain': 35},
            {'temp': 40, 'rain': 25},
            {'temp': 42, 'rain': 15},
            {'temp': 45, 'rain': 10},
            {'temp': 48, 'rain': 5},
        ],
        'forecast': [
            {'day': 'Today', 'high': 56, 'low': 40, 'icon': 'partly_cloudy_day'},
            {'day': 'Thu', 'high': 52, 'low': 38, 'icon': 'rain_day'},
            {'day': 'Fri', 'high': 48, 'low': 35, 'icon': 'cloudy'},
            {'day': 'Sat', 'high': 45, 'low': 32, 'icon': 'clear_day'},
            {'day': 'Sun', 'high': 50, 'low': 36, 'icon': 'partly_cloudy_day'},
            {'day': 'Mon', 'high': 54, 'low': 40, 'icon': 'partly_cloudy_day'},
        ]
    }

    # Create image with gradient background
    img = Image.new('RGB', (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for y in range(HEIGHT):
        factor = y / HEIGHT
        r = int(DARK_BLUE[0] * (1 - factor))
        g = int(DARK_BLUE[1] * (1 - factor))
        b = int(DARK_BLUE[2] * (1 - factor))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Header
    location = f"{data['city']}, {data['state']}"
    bbox = draw.textbbox((0, 0), location, font=fonts['location'])
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    draw.text((x, 22), location, font=fonts['location'], fill=WHITE)

    bbox = draw.textbbox((0, 0), data['date'], font=fonts['date'])
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    draw.text((x, 58), data['date'], font=fonts['date'], fill=TEXT_SECONDARY)

    draw.text((WIDTH - 80 - len(data['time'])*8, 22), data['time'], font=fonts['date'], fill=TEXT_SECONDARY)

    # Main weather icon
    icon = load_icon('partly_cloudy_day', 152)
    img.paste(icon, (60, 82), icon)

    # Temperature
    temp_str = str(data['temp'])
    draw.text((232, 100), temp_str, font=fonts['temp_large'], fill=WHITE)
    bbox = draw.textbbox((232, 100), temp_str, font=fonts['temp_large'])
    draw.text((bbox[2] + 2, 100), "°F", font=fonts['temp_unit'], fill=WHITE)

    draw.text((232, 194), data['desc'], font=fonts['description'], fill=TEXT_SECONDARY)
    draw.text((232, 216), f"Feels Like {data['feels']}°", font=fonts['feels'], fill=TEXT_SECONDARY)

    # Details
    col1_x, col2_x = 430, 590
    y_start = 90
    spacing = 50

    details = [
        (col1_x, 'sunrise', 'Sunrise', data['sunrise']),
        (col1_x, 'wind', 'Wind', f"{data['wind']:.1f} mph"),
        (col1_x, 'visibility', 'Visibility', f"{data['visibility']:.1f} mi"),
        (col2_x, 'sunset', 'Sunset', data['sunset']),
        (col2_x, 'humidity', 'Humidity', f"{data['humidity']} %"),
        (col2_x, 'aqi', 'Air Quality', f"{data['aqi']} /10"),
    ]

    for i, (x, icon_name, label, value) in enumerate(details):
        y = y_start + (i % 3) * spacing
        icon = load_icon(icon_name, 38)
        img.paste(icon, (x, y), icon)
        draw.text((x + 44, y + 4), label, font=fonts['detail_label'], fill=TEXT_SECONDARY)
        draw.text((x + 44, y + 20), value, font=fonts['detail_value'], fill=WHITE)

    # Graph
    graph_x, graph_y = 85, 257
    graph_w, graph_h = 590, 80

    hourly = data['hourly']
    temps = [h['temp'] for h in hourly]
    temp_min, temp_max = min(temps), max(temps)
    temp_range = temp_max - temp_min or 1

    # Y-axis labels
    draw.text((42, graph_y - 5), f"{temp_max}°F", font=fonts['axis'], fill=TEXT_SECONDARY)
    draw.text((42, graph_y + graph_h - 8), f"{temp_min}°F", font=fonts['axis'], fill=TEXT_SECONDARY)
    draw.text((graph_x + graph_w + 8, graph_y - 5), "100%", font=fonts['axis'], fill=TEXT_SECONDARY)
    draw.text((graph_x + graph_w + 8, graph_y + graph_h - 8), "0%", font=fonts['axis'], fill=TEXT_SECONDARY)

    step = graph_w / (len(temps) - 1)

    # Temperature line
    temp_points = [(int(graph_x + i * step), int(graph_y + graph_h - ((t - temp_min) / temp_range) * graph_h)) for i, t in enumerate(temps)]
    smooth_temp = bezier_curve(temp_points)

    # Orange gradient fill
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for layer in range(30):
        alpha = int(80 * (1 - layer / 30))
        y_offset = int((graph_h * layer) / 30)
        pts = [(px, py + y_offset) for px, py in smooth_temp]
        pts.append((smooth_temp[-1][0], graph_y + graph_h))
        pts.append((smooth_temp[0][0], graph_y + graph_h))
        overlay_draw.polygon(pts, fill=(*ORANGE, alpha))
    img.paste(overlay, (0, 0), overlay)

    for i in range(len(smooth_temp) - 1):
        draw.line([smooth_temp[i], smooth_temp[i + 1]], fill=ORANGE, width=3)

    # Rain line
    rain_points = [(int(graph_x + i * step), int(graph_y + graph_h - (h['rain'] / 100) * graph_h)) for i, h in enumerate(hourly)]
    smooth_rain = bezier_curve(rain_points)

    # Blue gradient fill
    rain_overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    rain_draw = ImageDraw.Draw(rain_overlay)
    for layer in range(30):
        alpha = int(60 * (1 - layer / 30))
        y_offset = int((graph_h * layer) / 30)
        pts = [(px, py + y_offset) for px, py in smooth_rain]
        pts.append((smooth_rain[-1][0], graph_y + graph_h))
        pts.append((smooth_rain[0][0], graph_y + graph_h))
        rain_draw.polygon(pts, fill=(*BLUE, alpha))
    img.paste(rain_overlay, (0, 0), rain_overlay)

    for i in range(len(smooth_rain) - 1):
        draw.line([smooth_rain[i], smooth_rain[i + 1]], fill=BLUE, width=2)

    # X-axis labels
    times = ['Now', '+3h', '+6h', '+9h', '+12h', '+15h', '+18h', '+21h', '+24h', '+27h', '+30h']
    for i, t in enumerate(times[:len(hourly)]):
        px = graph_x + i * step
        draw.text((px, graph_y + graph_h + 5), t, font=fonts['axis'], fill=TEXT_SECONDARY, anchor='mt')

    # Forecast cards
    y_start = 370
    card_w = (WIDTH - 100) // 6
    x_start = 50

    for i, day in enumerate(data['forecast']):
        x = x_start + i * card_w

        # Card background
        draw.rounded_rectangle([x, y_start, x + card_w - 8, HEIGHT - 15], radius=8, fill=(30, 35, 50), outline=(60, 65, 80))

        # Day name
        bbox = draw.textbbox((0, 0), day['day'], font=fonts['forecast_day'])
        text_w = bbox[2] - bbox[0]
        draw.text((x + (card_w - 8 - text_w) // 2, y_start + 8), day['day'], font=fonts['forecast_day'], fill=WHITE)

        # Icon
        icon = load_icon(day['icon'], 40)
        img.paste(icon, (x + (card_w - 48) // 2, y_start + 30), icon)

        # Temps
        high = f"{day['high']}°"
        low = f"{day['low']}°"
        bbox = draw.textbbox((0, 0), high, font=fonts['forecast_temp'])
        draw.text((x + (card_w - 8 - (bbox[2] - bbox[0])) // 2, y_start + 75), high, font=fonts['forecast_temp'], fill=WHITE)
        bbox = draw.textbbox((0, 0), low, font=fonts['forecast_temp'])
        draw.text((x + (card_w - 8 - (bbox[2] - bbox[0])) // 2, y_start + 92), low, font=fonts['forecast_temp'], fill=BLUE)

    # Enhance
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Color(img).enhance(1.3)

    # Save
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output = os.path.join(script_dir, 'screenshot.png')
    img.save(output)
    print(f"Screenshot saved: {output}")


if __name__ == '__main__':
    create_screenshot()
