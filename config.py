import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY_NAME = os.getenv('CITY_NAME', 'London')
COUNTRY_CODE = os.getenv('COUNTRY_CODE', 'UK')
UNITS = os.getenv('UNITS', 'metric')  # metric, imperial, or kelvin

# Display configuration
UPDATE_INTERVAL_MINUTES = 20
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 480

# Weather display settings
SHOW_CURRENT_WEATHER = True
SHOW_FORECAST = True
FORECAST_DAYS = 3
SHOW_HUMIDITY = True
SHOW_WIND = True
SHOW_PRESSURE = True

# Colors for Inky Impression (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
