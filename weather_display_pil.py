#!/usr/bin/env python3
"""
PIL-based Weather Display for Inky Impression
Renders weather dashboard with actual PNG icons to match HTML design
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from inky.auto import auto
from datetime import datetime
import os


def get_weather_icon(icon_code, wind_speed=0):
    """Map OpenWeatherMap icon code to local icon filename.

    Args:
        icon_code: OpenWeatherMap icon code (e.g., '01d', '01n', '10d')
        wind_speed: Current wind speed in mph for windy icon logic

    Returns:
        str: Local icon filename
    """
    # Very high wind (>= 20mph) overrides all weather icons
    if wind_speed >= 20:
        return "windy"

    is_night = icon_code.endswith('n')
    base_code = icon_code[:2]

    # Icon mapping based on OpenWeatherMap codes
    # 01 = clear sky
    if base_code == '01':
        if is_night:
            return "clear_night"
        else:
            # Clear day with wind >= 10mph uses windy variant
            if wind_speed >= 10:
                return "clear_windy"
            return "clear_day"

    # 02 = few clouds (partly cloudy)
    elif base_code == '02':
        if is_night:
            return "partly_cloudy_night"
        else:
            return "partly_cloudy_day"

    # 03 = scattered clouds, 04 = broken clouds (cloudy)
    elif base_code in ('03', '04'):
        # Cloudy with wind >= 10mph during day uses windy variant
        if not is_night and wind_speed >= 10:
            return "cloudy_windy"
        return "cloudy"

    # 09 = shower rain / drizzle
    elif base_code == '09':
        if is_night:
            return "drizzle_night"
        else:
            return "drizzle_day"

    # 10 = rain
    elif base_code == '10':
        if is_night:
            return "rain_night"
        else:
            return "rain_day"

    # 11 = thunderstorm
    elif base_code == '11':
        return "thunderstorm"

    # 13 = snow
    elif base_code == '13':
        if is_night:
            return "snow_night"
        else:
            return "snow_day"

    # 50 = mist/fog
    elif base_code == '50':
        return "mist"

    # Default fallback
    else:
        return "cloudy"


def bezier_curve(points, num_segments=50):
    """Generate smooth bezier curve points from a list of control points using Catmull-Rom splines"""
    if len(points) < 2:
        return points

    result = []

    # Catmull-Rom spline interpolation
    for i in range(len(points) - 1):
        # Get 4 points for the spline (with boundary handling)
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]

        # Generate points along this segment
        for t_step in range(num_segments):
            t = t_step / num_segments
            t2 = t * t
            t3 = t2 * t

            # Catmull-Rom basis functions
            x = 0.5 * ((2 * p1[0]) +
                      (-p0[0] + p2[0]) * t +
                      (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                      (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)

            y = 0.5 * ((2 * p1[1]) +
                      (-p0[1] + p2[1]) * t +
                      (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                      (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)

            result.append((int(x), int(y)))

    # Add the last point
    result.append(points[-1])

    return result

class WeatherDisplay:
    def __init__(self):
        try:
            self.display = auto()
            print(f"Detected display: {self.display.resolution}")
        except Exception as e:
            print(f"Error initializing display: {e}")
            print("Make sure your Inky Impression is properly connected")
            raise

        # Display dimensions
        self.width = self.display.width
        self.height = self.display.height

        # Colors - Matte dark theme (reduces glare)
        self.WHITE = (255, 255, 255)  # Text color
        self.BLACK = (0, 0, 0)           # Pure black
        self.DARK_BLUE = (5, 8, 15)      # Very dark blue, almost black
        self.BORDER = (100, 100, 120)  # Lighter border for dark mode
        self.TEXT_SECONDARY = (200, 200, 220)  # Slightly dimmed text

        # Try to load Inter fonts (fallback to DejaVu if not available)
        try:
            # Try Inter first - adjusted sizes
            self.font_location = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Bold.ttf", 30)
            self.font_date = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 17)
            self.font_temp_large = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 90)
            self.font_temp_unit = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 42)
            self.font_feels = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 16)
            self.font_description = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Medium.ttf", 17)
            self.font_detail_label = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 13)
            self.font_detail_value = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Bold.ttf", 18)
            self.font_forecast_day = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Bold.ttf", 16)
            self.font_forecast_temp = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Medium.ttf", 13)
            self.font_axis = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 11)
            self.font_footer = ImageFont.truetype("/usr/share/fonts/truetype/inter/Inter-Regular.ttf", 8)
        except:
            try:
                # Fallback to DejaVu - adjusted sizes
                self.font_location = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
                self.font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
                self.font_temp_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 90)
                self.font_temp_unit = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
                self.font_feels = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                self.font_description = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
                self.font_detail_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
                self.font_detail_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                self.font_forecast_day = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
                self.font_forecast_temp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
                self.font_axis = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
                self.font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
            except Exception as e:
                print(f"Warning: Could not load fonts: {e}")
                print("Using default fonts")
                # Fallback to default
                self.font_location = ImageFont.load_default()
                self.font_date = ImageFont.load_default()
                self.font_temp_large = ImageFont.load_default()
                self.font_temp_unit = ImageFont.load_default()
                self.font_feels = ImageFont.load_default()
                self.font_detail_label = ImageFont.load_default()
                self.font_detail_value = ImageFont.load_default()
                self.font_forecast_day = ImageFont.load_default()
                self.font_forecast_temp = ImageFont.load_default()
                self.font_axis = ImageFont.load_default()
                self.font_footer = ImageFont.load_default()

    def load_icon(self, icon_name, size, wind_speed=0, force_day=False):
        """Load and resize an icon with high quality

        Args:
            icon_name: The icon code (e.g., '01d', '01n') or UI icon name (e.g., 'sunrise')
            size: The size to resize the icon to
            wind_speed: Current wind speed for weather icon wind variants
            force_day: If True, always convert night icons to day versions (for forecasts)
        """
        # UI icons are loaded directly by name
        ui_icons = ['sunrise', 'sunset', 'wind', 'humidity', 'visibility', 'aqi']

        is_ui_icon = icon_name in ui_icons
        if is_ui_icon:
            icon_path = f"icons/{icon_name}.png"
            print(f"  Loading UI icon: {icon_name}")
        else:
            # Weather icon - use mapping function
            if force_day and icon_name.endswith('n'):
                # For forecast cards, convert to day version
                icon_name = icon_name[:-1] + 'd'
                print(f"  Converting to day icon for forecast: {icon_name}")

            mapped_icon = get_weather_icon(icon_name, wind_speed)
            icon_path = f"icons/{mapped_icon}.png"
            print(f"  Loading weather icon: {icon_name} -> {mapped_icon}")

        if not os.path.exists(icon_path):
            print(f"Warning: Icon {icon_path} not found")
            # Return a blank image
            return Image.new('RGBA', (size, size), (255, 255, 255, 0))

        try:
            icon = Image.open(icon_path)
            # Convert to RGBA if needed
            if icon.mode != 'RGBA':
                icon = icon.convert('RGBA')

            # Use high-quality resize instead of thumbnail
            icon = icon.resize((size, size), Image.Resampling.LANCZOS)

            # Enhance sharpness for better display on e-ink
            enhancer = ImageEnhance.Sharpness(icon)
            icon = enhancer.enhance(1.5)  # Increase sharpness by 50%

            # Boost color saturation for vibrant icons
            color_enhancer = ImageEnhance.Color(icon)
            icon = color_enhancer.enhance(1.8)  # 80% more saturated

            # Boost contrast for icons to make them pop
            contrast_enhancer = ImageEnhance.Contrast(icon)
            icon = contrast_enhancer.enhance(1.5)  # 50% more contrast

            # Extra enhancement for small UI icons
            if is_ui_icon:
                # Reduce brightness to deepen colors
                brightness_enhancer = ImageEnhance.Brightness(icon)
                icon = brightness_enhancer.enhance(0.85)  # 15% darker

                # High contrast to make colors pop
                contrast_enhancer2 = ImageEnhance.Contrast(icon)
                icon = contrast_enhancer2.enhance(2.0)  # Double contrast

                # Extra saturation boost for UI icons
                color_enhancer2 = ImageEnhance.Color(icon)
                icon = color_enhancer2.enhance(2.2)  # More than double saturation

            # Make sunrise and sunset icons completely yellow
            if icon_name in ('sunrise', 'sunset'):
                icon = self.make_icon_yellow(icon)

            return icon
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")
            return Image.new('RGBA', (size, size), (255, 255, 255, 0))

    def make_icon_yellow(self, icon):
        """Convert icon colors to yellow while preserving transparency"""
        if icon.mode != 'RGBA':
            icon = icon.convert('RGBA')

        pixels = icon.load()
        width, height = icon.size

        # Yellow color (RGB: 255, 220, 0)
        yellow = (255, 220, 0)

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]

                # Only modify non-transparent pixels
                if a > 0:
                    # Calculate brightness of original pixel
                    brightness = (r + g + b) / 3 / 255

                    # Apply yellow with original brightness
                    new_r = int(yellow[0] * brightness)
                    new_g = int(yellow[1] * brightness)
                    new_b = int(yellow[2] * brightness)

                    pixels[x, y] = (new_r, new_g, new_b, a)

        return icon

    def draw_header(self, draw, city, country, current_date, last_updated):
        """Draw centered header with location and date, timestamp in top right"""
        # Location - shifted down slightly more
        location = f"{city}, {country}"
        bbox = draw.textbbox((0, 0), location, font=self.font_location)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        location_y = 22
        draw.text((x, location_y), location, font=self.font_location, fill=self.WHITE)

        # Date - shifted down slightly more
        bbox = draw.textbbox((0, 0), current_date, font=self.font_date)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, 58), current_date, font=self.font_date, fill=self.TEXT_SECONDARY)

        # Timestamp in top right corner, even with location
        bbox = draw.textbbox((0, 0), last_updated, font=self.font_date)
        text_width = bbox[2] - bbox[0]
        draw.text((self.width - text_width - 80, location_y), last_updated,
                 font=self.font_date, fill=self.TEXT_SECONDARY)

    def draw_current_weather(self, img, draw, weather_data, y_start=100):
        """Draw current weather section with icon and temperature"""
        current = weather_data['current']

        # Left side - icon moved up and left slightly
        wind_speed = current.get('wind_speed', 0)
        print(f"Loading MAIN weather icon: {current['icon']} (wind_speed={wind_speed})")
        icon = self.load_icon(current['icon'], 152, wind_speed=wind_speed)
        img.paste(icon, (60, y_start - 18), icon if icon.mode == 'RGBA' else None)

        # Temperature - moved up more
        temp_x = 232
        temp_y = y_start

        # Main temperature (just the number)
        temp_text = f"{current['temperature']}"
        draw.text((temp_x, temp_y), temp_text, font=self.font_temp_large, fill=self.WHITE)

        # Get the width of the temperature number to position degree symbol
        bbox = draw.textbbox((temp_x, temp_y), temp_text, font=self.font_temp_large)
        degree_x = bbox[2] + 2

        # Degree symbol and F (proper sizing)
        draw.text((degree_x, temp_y), "°F", font=self.font_temp_unit, fill=self.WHITE)

        # Weather description - shifted down more for bigger temp
        description_text = current.get('description', 'Clear')
        draw.text((temp_x, temp_y + 94), description_text, font=self.font_description, fill=self.TEXT_SECONDARY)

        # Feels like - shifted down more for bigger temp
        feels_text = f"Feels Like {current['feels_like']}°"
        draw.text((temp_x, temp_y + 116), feels_text, font=self.font_feels, fill=self.TEXT_SECONDARY)

    def draw_details(self, img, draw, weather_data, y_start=90):
        """Draw two columns of weather details with icons"""
        current = weather_data['current']

        # Column positions - shifted right to use freed space
        col1_x = 430
        col2_x = 590
        detail_y = y_start
        row_spacing = 50  # More vertical spacing between rows

        # Column 1 details
        details_col1 = [
            ('sunrise', 'Sunrise', current['sunrise'].strftime('%I:%M %p').lstrip('0')),
            ('wind', 'Wind', f"{current['wind_speed']:.1f} mph"),
            ('visibility', 'Visibility', f"{current.get('visibility', 10):.1f} mi"),
        ]

        # Column 2 details
        details_col2 = [
            ('sunset', 'Sunset', current['sunset'].strftime('%I:%M %p').lstrip('0')),
            ('humidity', 'Humidity', f"{current['humidity']} %"),
            ('aqi', 'Air Quality', f"{current.get('air_quality', {}).get('index', 0)} /10"),
        ]

        # Draw column 1 - tighter spacing between icon and text
        for i, (icon_name, label, value) in enumerate(details_col1):
            y = detail_y + i * row_spacing
            # Load and paste icon (38x38)
            icon = self.load_icon(icon_name, 38)
            img.paste(icon, (col1_x, y), icon if icon.mode == 'RGBA' else None)
            # Draw label and value - adjusted for larger icon
            draw.text((col1_x + 44, y + 4), label, font=self.font_detail_label, fill=self.TEXT_SECONDARY)
            draw.text((col1_x + 44, y + 20), value, font=self.font_detail_value, fill=self.WHITE)

        # Draw column 2 - tighter spacing between icon and text
        for i, (icon_name, label, value) in enumerate(details_col2):
            y = detail_y + i * row_spacing
            # Load and paste icon (38x38)
            icon = self.load_icon(icon_name, 38)
            img.paste(icon, (col2_x, y), icon if icon.mode == 'RGBA' else None)
            # Draw label and value - adjusted for larger icon
            draw.text((col2_x + 44, y + 4), label, font=self.font_detail_label, fill=self.TEXT_SECONDARY)
            draw.text((col2_x + 44, y + 20), value, font=self.font_detail_value, fill=self.WHITE)

    def draw_graph_section(self, img, draw, hourly_data, temp_min, temp_max, y_start=245):
        """Draw temperature graph with time labels"""
        if not hourly_data or len(hourly_data) < 2:
            return

        # Graph dimensions - shifted up, compressed from right
        graph_x = 85  # Start position for graph line
        graph_width = 590  # Compressed width from right side
        graph_height = 80  # Increased height
        graph_y = y_start + 12

        # No border/background - just draw on white canvas

        # Y-axis labels (left - temperature) - outside graph area
        draw.text((42, graph_y - 5), f"{temp_max}°F", font=self.font_detail_label, fill=self.TEXT_SECONDARY)
        draw.text((42, graph_y + graph_height - 8), f"{temp_min}°F", font=self.font_detail_label, fill=self.TEXT_SECONDARY)

        # Y-axis labels (right - rain %) - outside graph area, won't overlap
        draw.text((graph_x + graph_width + 8, graph_y - 5), "100%", font=self.font_detail_label, fill=self.TEXT_SECONDARY)
        draw.text((graph_x + graph_width + 8, graph_y + graph_height - 8), "0%", font=self.font_detail_label, fill=self.TEXT_SECONDARY)

        # Calculate points for temperature line
        temps = [h['temp'] for h in hourly_data]
        temp_range = temp_max - temp_min if temp_max != temp_min else 1

        points = []
        step = graph_width / (len(temps) - 1) if len(temps) > 1 else graph_width

        for i, temp in enumerate(temps):
            px = graph_x + i * step
            # Invert y (higher temp = higher on screen)
            py = graph_y + graph_height - ((temp - temp_min) / temp_range) * graph_height
            points.append((int(px), int(py)))

        # Draw gradient fill under the temperature line using alpha blending
        ORANGE = (255, 140, 66)
        BLUE = (100, 150, 255)

        # Generate smooth curve points using bezier interpolation
        smooth_temp_points = bezier_curve(points, num_segments=20) if len(points) > 1 else points

        if len(smooth_temp_points) > 1:
            # Create a temporary RGBA image for the gradient
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)

            # Draw multiple layers with decreasing opacity to create gradient
            num_layers = 30
            for layer in range(num_layers):
                # Calculate alpha (more transparent as we go down)
                alpha = int(80 * (1 - layer / num_layers))

                # Calculate Y offset for this layer
                y_offset = int((graph_height * layer) / num_layers)

                # Create polygon points for this layer using smooth curve
                layer_points = []
                for px, py in smooth_temp_points:
                    layer_points.append((px, py + y_offset))

                # Add bottom edge
                layer_points.append((int(smooth_temp_points[-1][0]), int(graph_y + graph_height)))
                layer_points.append((int(smooth_temp_points[0][0]), int(graph_y + graph_height)))

                # Draw this layer
                overlay_draw.polygon(layer_points, fill=(*ORANGE, alpha))

            # Paste the gradient overlay onto the main image
            img.paste(overlay, (0, 0), overlay)

            # Draw the smooth temperature line on top
            for i in range(len(smooth_temp_points) - 1):
                draw.line([smooth_temp_points[i], smooth_temp_points[i + 1]], fill=ORANGE, width=3)

        # Calculate points for precipitation line chart
        rain_points = []
        for i, hour in enumerate(hourly_data):
            rain_pct = hour.get('rain_chance', 0)
            px = graph_x + i * step
            # Y position based on rain percentage (0% at bottom, 100% at top)
            py = graph_y + graph_height - (rain_pct / 100) * graph_height
            rain_points.append((int(px), int(py)))

        # Generate smooth curve for precipitation line
        if len(rain_points) > 1:
            smooth_rain_points = bezier_curve(rain_points, num_segments=20)

            # Create a temporary RGBA image for the blue gradient under precipitation line
            rain_overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            rain_overlay_draw = ImageDraw.Draw(rain_overlay)

            # Draw multiple layers with decreasing opacity to create gradient
            num_layers = 30
            for layer in range(num_layers):
                # Calculate alpha (more transparent as we go down)
                alpha = int(80 * (1 - layer / num_layers))

                # Calculate Y offset for this layer
                y_offset = int((graph_height * layer) / num_layers)

                # Create polygon points for this layer using smooth curve
                layer_points = []
                for px, py in smooth_rain_points:
                    layer_points.append((px, py + y_offset))

                # Add bottom edge
                layer_points.append((int(smooth_rain_points[-1][0]), int(graph_y + graph_height)))
                layer_points.append((int(smooth_rain_points[0][0]), int(graph_y + graph_height)))

                # Draw this layer in blue
                rain_overlay_draw.polygon(layer_points, fill=(*BLUE, alpha))

            # Paste the blue gradient overlay onto the main image
            img.paste(rain_overlay, (0, 0), rain_overlay)

            # Draw the smooth precipitation line on top
            for i in range(len(smooth_rain_points) - 1):
                draw.line([smooth_rain_points[i], smooth_rain_points[i + 1]], fill=BLUE, width=2)

        # Time labels below graph - show all time points (every 3 hours from API)
        label_y = graph_y + graph_height + 10
        for i, hour in enumerate(hourly_data):
            px = graph_x + i * step
            time_text = hour['time']
            bbox = draw.textbbox((0, 0), time_text, font=self.font_axis)
            text_width = bbox[2] - bbox[0]
            draw.text((int(px - text_width // 2), label_y), time_text,
                     font=self.font_axis, fill=self.TEXT_SECONDARY)

    def draw_forecast(self, img, draw, forecast_data, y_start=370):
        """Draw forecast cards starting with Today (6 days total)"""
        if not forecast_data:
            print("Warning: No forecast data available")
            return

        # Show 6 days starting with today (indices 0-5)
        # This gives us: Today, Tomorrow, Day+2, Day+3, Day+4, Day+5
        daily_forecasts = forecast_data[0:6]  # Get first 6 days including today
        if not daily_forecasts:
            print("Warning: No daily forecasts in data")
            return

        # Debug output to verify we're showing the right days
        print(f"Drawing {len(daily_forecasts)} forecast cards (starting with today)")
        if daily_forecasts:
            print(f"First card date: {daily_forecasts[0].get('date', 'Unknown')} ({daily_forecasts[0].get('day_name', 'Unknown')})")
            print(f"Last card date: {daily_forecasts[-1].get('date', 'Unknown')} ({daily_forecasts[-1].get('day_name', 'Unknown')})")

        # Calculate card dimensions - maximum compression horizontally
        cards_per_row = len(daily_forecasts)
        total_spacing = 58 * 2  # Even larger left and right padding for smaller cards
        gap_spacing = 3 * (cards_per_row - 1)  # Minimal spacing between cards
        available_width = self.width - total_spacing - gap_spacing
        card_width = available_width // cards_per_row
        card_height = 90  # Smaller height

        for i, day in enumerate(daily_forecasts):
            card_x = 42 + i * (card_width + 3)  # Shifted right two tads
            # Override day name for first card to show "Today"
            day_display = day.copy()
            if i == 0:
                day_display['day_name'] = 'Today'
            print(f"Forecast day {i}: {day_display.get('day_name', 'Unknown')} - Icon: {day.get('icon', 'N/A')}")
            self.draw_forecast_card(img, draw, day_display, card_x, y_start, card_width, card_height)

    def draw_forecast_card(self, img, draw, day_data, x, y, width, height):
        """Draw a single forecast card with rounded corners"""
        # Draw rounded rectangle by drawing a rectangle and circles at corners
        radius = 8  # Slightly smaller radius

        # Main rectangle body - semi-transparent dark background
        card_bg = (15, 20, 30)  # Very dark blue
        draw.rectangle([x + radius, y, x + width - radius, y + height],
                      fill=card_bg, outline=None)
        draw.rectangle([x, y + radius, x + width, y + height - radius],
                      fill=card_bg, outline=None)

        # Draw border with lighter color for dark mode
        # Top and bottom lines
        draw.line([(x + radius, y), (x + width - radius, y)], fill=self.BORDER, width=2)
        draw.line([(x + radius, y + height), (x + width - radius, y + height)], fill=self.BORDER, width=2)
        # Left and right lines
        draw.line([(x, y + radius), (x, y + height - radius)], fill=self.BORDER, width=2)
        draw.line([(x + width, y + radius), (x + width, y + height - radius)], fill=self.BORDER, width=2)

        # Draw corner arcs
        draw.arc([x, y, x + radius*2, y + radius*2], start=180, end=270, fill=self.BORDER, width=2)
        draw.arc([x + width - radius*2, y, x + width, y + radius*2], start=270, end=360, fill=self.BORDER, width=2)
        draw.arc([x, y + height - radius*2, x + radius*2, y + height], start=90, end=180, fill=self.BORDER, width=2)
        draw.arc([x + width - radius*2, y + height - radius*2, x + width, y + height], start=0, end=90, fill=self.BORDER, width=2)

        # Day name (centered)
        day_name = day_data['day_name']
        bbox = draw.textbbox((0, 0), day_name, font=self.font_forecast_day)
        text_width = bbox[2] - bbox[0]
        draw.text((x + (width - text_width) // 2, y + 6), day_name,
                 font=self.font_forecast_day, fill=self.WHITE)

        # Weather icon (centered, 46x46)
        icon_size = 46
        icon_code = day_data.get('icon', '01d')

        print(f"  Loading icon: {icon_code} at size {icon_size}")

        icon = self.load_icon(icon_code, icon_size, wind_speed=0, force_day=True)
        icon_x = int(x + (width - icon_size) // 2)
        icon_y = int(y + 25)

        # Convert icon to have proper alpha channel and paste
        if icon:
            try:
                # Ensure icon is in RGBA mode
                if icon.mode != 'RGBA':
                    icon = icon.convert('RGBA')

                # Paste icon with transparency support
                img.paste(icon, (icon_x, icon_y), icon)
                print(f"  Icon pasted at ({icon_x}, {icon_y})")
            except Exception as e:
                print(f"  Error pasting icon: {e}")
                # Draw a placeholder circle if icon fails
                draw.ellipse([icon_x, icon_y, icon_x + 40, icon_y + 40],
                           outline=self.BLACK, width=2)

        # Temperature range (centered, adjusted for smaller card)
        temp_text = f"{day_data['max_temp']} / {day_data['min_temp']}°"
        bbox = draw.textbbox((0, 0), temp_text, font=self.font_forecast_temp)
        text_width = bbox[2] - bbox[0]
        draw.text((x + (width - text_width) // 2, y + 73), temp_text,
                 font=self.font_forecast_temp, fill=self.WHITE)

    def prepare_template_data(self, weather_data):
        """Prepare data for display rendering"""
        if not weather_data or not weather_data.get('current'):
            return None

        current = weather_data['current']
        forecast = weather_data.get('forecast', {})

        # Format hourly data for graph
        hourly_data = []
        if forecast.get('hourly'):
            for i, hour in enumerate(forecast['hourly'][:8]):  # Take 8 points for 24 hours
                # First point is "Now" (current weather), rest are 3-hour forecast intervals
                time_label = "Now" if i == 0 else hour['time'].strftime('%I %p').lstrip('0').lower()
                hourly_data.append({
                    'time': time_label,
                    'temp': hour['temp'],
                    'rain_chance': hour.get('rain_chance', 0)  # Probability of precipitation
                })

        # Calculate temp range for graph scaling
        temps = [h['temp'] for h in hourly_data] if hourly_data else [current['temperature']]
        temp_min = min(temps)
        temp_max = max(temps)

        # Format state code (convert country to state if US)
        state = current.get('country', 'US')
        if state == 'US':
            state = 'PA'  # Default to PA for Conshohocken

        return {
            'city': current['city'],
            'country': state,
            'current_date': current['timestamp'].strftime('%A, %B %d'),
            'current': current,
            'hourly_data': hourly_data,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'forecast': forecast.get('daily', [])[:7],
            'last_updated': weather_data.get('last_updated', datetime.now()).strftime('%I:%M%p').lstrip('0').lower()
        }

    def update_display(self, weather_data):
        """Update the display with weather data"""
        try:
            if not weather_data or not weather_data.get('current'):
                print("No weather data available")
                return

            # Prepare data
            data = self.prepare_template_data(weather_data)
            if not data:
                print("Could not prepare template data")
                return

            # Create image with dark gradient background
            img = Image.new("RGB", (self.width, self.height))
            draw = ImageDraw.Draw(img)

            # Draw gradient background from dark blue/black to black
            for y in range(self.height):
                # Calculate gradient factor (0 at top, 1 at bottom)
                factor = y / self.height
                # Interpolate between DARK_BLUE and BLACK
                r = int(self.DARK_BLUE[0] * (1 - factor) + self.BLACK[0] * factor)
                g = int(self.DARK_BLUE[1] * (1 - factor) + self.BLACK[1] * factor)
                b = int(self.DARK_BLUE[2] * (1 - factor) + self.BLACK[2] * factor)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))

            # Draw all sections
            self.draw_header(draw, data['city'], data['country'], data['current_date'], data['last_updated'])
            self.draw_current_weather(img, draw, data, y_start=100)
            self.draw_details(img, draw, data, y_start=90)
            self.draw_graph_section(img, draw, data['hourly_data'], data['temp_min'], data['temp_max'], y_start=245)
            self.draw_forecast(img, draw, data['forecast'], y_start=370)

            # Enhance contrast for e-ink display
            # Increase contrast for better visibility
            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(1.4)  # 40% more contrast

            # Boost color saturation for more vivid icons
            color_enhancer = ImageEnhance.Color(img)
            img = color_enhancer.enhance(1.3)  # 30% more saturated

            # Save for debugging
            img.save('weather_display.png')
            print(f"Weather display saved as weather_display.png")

            # Display on e-ink
            self.display.set_image(img)
            self.display.show()

            print(f"Weather display updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            print(f"Error updating display: {e}")
            import traceback
            traceback.print_exc()


def test_display():
    """Test function to verify display is working"""
    from datetime import timedelta
    try:
        display = WeatherDisplay()
        print("✅ Display initialized successfully")

        # Sample rain chances - starts low, increases tonight, then decreases
        rain_chances = [5, 10, 15, 25, 35, 40, 35, 25, 15, 10, 5]

        # Test with sample data
        test_data = {
            'current': {
                'city': 'Philadelphia',
                'country': 'US',
                'temperature': 54,
                'feels_like': 51,
                'temp_min': 51,
                'temp_max': 56,
                'description': 'Partly Cloudy',
                'icon': '02d',
                'humidity': 60,
                'wind_speed': 5.99,
                'wind_direction': 180,
                'pressure': 1016,
                'sunrise': datetime.now().replace(hour=7, minute=20),
                'sunset': datetime.now().replace(hour=18, minute=10),
                'visibility': 10.0,
                'uv_index': 2.9,
                'air_quality': {'index': 2, 'description': 'Fair'},
                'timestamp': datetime.now()
            },
            'forecast': {
                'hourly': [
                    {
                        'time': datetime.now() + timedelta(hours=i*3),
                        'temp': 50 + i,
                        'icon': '02d',
                        'rain_chance': rain_chances[i]
                    }
                    for i in range(11)
                ],
                'daily': [
                    {
                        'date': datetime.now().date() + timedelta(days=i),
                        'day_name': ['Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu'][i],
                        'min_temp': 46 + i,
                        'max_temp': 54 + i,
                        'description': 'Partly Cloudy',
                        'icon': '02d',
                        'humidity': 60,
                        'wind_speed': 5.99
                    }
                    for i in range(7)
                ]
            },
            'last_updated': datetime.now()
        }

        display.update_display(test_data)
        print("✅ Test display update completed")

    except Exception as e:
        print(f"❌ Display test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_display()
