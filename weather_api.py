import requests
import json
from datetime import datetime, timedelta
from config import OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE, UNITS

class WeatherAPI:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.city = CITY_NAME
        self.country = COUNTRY_CODE
        self.units = UNITS
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY in your .env file")
    
    def get_current_weather(self):
        """Fetch current weather data"""
        url = f"{self.base_url}/weather"
        params = {
            'q': f"{self.city},{self.country}",
            'appid': self.api_key,
            'units': self.units
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Get coordinates for additional API calls
            lat = data['coord']['lat']
            lon = data['coord']['lon']

            # Fetch UV index and air quality
            uv_index = self.get_uv_index(lat, lon)
            air_quality = self.get_air_quality(lat, lon)

            return {
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'temp_min': round(data['main']['temp_min']),
                'temp_max': round(data['main']['temp_max']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'city': data['name'],
                'country': data['sys']['country'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'uv_index': uv_index,
                'air_quality': air_quality,
                'timestamp': datetime.now(),
                'lat': lat,
                'lon': lon
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather: {e}")
            return None

    def get_uv_index(self, lat, lon):
        """Fetch UV index data"""
        try:
            # Note: OpenWeatherMap free tier may not support UV index
            # This is a placeholder - you may need One Call API
            url = f"http://api.openweathermap.org/data/2.5/uvi"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return round(data.get('value', 0), 1)
        except:
            pass
        return 0

    def get_air_quality(self, lat, lon):
        """Fetch air quality data"""
        try:
            url = f"{self.base_url}/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                aqi = data['list'][0]['main']['aqi']
                # Convert to descriptive text
                aqi_text = ['Good', 'Fair', 'Moderate', 'Poor', 'Very Poor']
                return {'index': aqi, 'description': aqi_text[min(aqi-1, 4)]}
        except:
            pass
        return {'index': 0, 'description': 'N/A'}
    
    def get_forecast(self, days=10):
        """Fetch weather forecast for specified number of days"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': f"{self.city},{self.country}",
            'appid': self.api_key,
            'units': self.units
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Group forecasts by day
            daily_forecasts = {}
            hourly_data = []

            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)

                    # Store hourly data for timeline (next 24 hours)
                # Only take 7 forecast points to leave room for "Now" point
                if len(hourly_data) < 7:
                    hourly_data.append({
                        'time': datetime.fromtimestamp(item['dt']),
                        'temp': round(item['main']['temp']),
                        'icon': item['weather'][0]['icon'],
                        'rain_chance': round(item.get('pop', 0) * 100)  # Probability of precipitation as percentage
                    })

            # Get daily summaries
            forecast_days = []
            print(f"Total forecast days available: {len(daily_forecasts)}")
            for i, (date, day_forecasts) in enumerate(list(daily_forecasts.items())[:days+1]):
                print(f"Processing day {i}: {date} ({date.strftime('%a')})")
                # Get min/max temps and most common weather
                temps = [f['main']['temp'] for f in day_forecasts]
                weather_conditions = [f['weather'][0]['description'] for f in day_forecasts]

                # Find most common weather condition
                most_common_weather = max(set(weather_conditions), key=weather_conditions.count)

                # Always use short day name (Mon, Tue, Wed, etc.)
                day_name = date.strftime('%a')

                forecast_days.append({
                    'date': date,
                    'day_name': day_name,
                    'min_temp': round(min(temps)),
                    'max_temp': round(max(temps)),
                    'description': most_common_weather.title(),
                    'icon': day_forecasts[0]['weather'][0]['icon'],
                    'humidity': round(sum(f['main']['humidity'] for f in day_forecasts) / len(day_forecasts)),
                    'wind_speed': round(sum(f['wind']['speed'] for f in day_forecasts) / len(day_forecasts), 1)
                })

            return {'daily': forecast_days, 'hourly': hourly_data}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast: {e}")
            return {'daily': [], 'hourly': []}
    
    def get_weather_data(self):
        """Get both current weather and forecast data"""
        current = self.get_current_weather()
        forecast = self.get_forecast()

        # Merge current weather into today's forecast for accurate today's data
        if current and forecast and forecast.get('daily') and len(forecast['daily']) > 0:
            today = datetime.now().date()
            first_forecast_date = forecast['daily'][0]['date']

            today_data = {
                'date': today,
                'day_name': today.strftime('%a'),
                'min_temp': current['temp_min'],
                'max_temp': current['temp_max'],
                'description': current['description'],
                'icon': current['icon'],
                'humidity': current['humidity'],
                'wind_speed': current['wind_speed']
            }

            # If first forecast is today, replace it with current weather data
            if first_forecast_date == today:
                forecast['daily'][0] = today_data
                print(f"Updated today's forecast with current weather data: {current['temp_min']}/{current['temp_max']}°F")
            else:
                # Today is missing from forecast (late night), insert it at the beginning
                forecast['daily'].insert(0, today_data)
                print(f"Inserted today's forecast from current weather: {current['temp_min']}/{current['temp_max']}°F")

        # Add current weather as the first point in hourly data for immediate graph relevance
        if current and forecast and forecast.get('hourly'):
            now_data = {
                'time': datetime.now(),
                'temp': current['temperature'],
                'icon': current['icon'],
                'rain_chance': 0  # Current weather doesn't have precipitation probability
            }
            forecast['hourly'].insert(0, now_data)
            print(f"Added 'Now' as first hourly point: {current['temperature']}°F")

        return {
            'current': current,
            'forecast': forecast,
            'last_updated': datetime.now()
        }

def test_weather_api():
    """Test function to verify API connection"""
    try:
        weather = WeatherAPI()
        data = weather.get_weather_data()
        
        if data['current']:
            print("✅ Weather API connection successful!")
            print(f"Current temperature in {data['current']['city']}: {data['current']['temperature']}°{UNITS.upper()}")
            print(f"Description: {data['current']['description']}")
        else:
            print("❌ Failed to fetch weather data")
            
    except Exception as e:
        print(f"❌ Error testing weather API: {e}")

if __name__ == "__main__":
    test_weather_api()
