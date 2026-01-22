#!/usr/bin/env python3
"""
Weather Dashboard for Raspberry Pi with Inky Impression Display
Updates every 30 minutes with current weather and forecast data
"""

import schedule
import time
import logging
from datetime import datetime
from weather_api import WeatherAPI
from weather_display_pil import WeatherDisplay
from config import UPDATE_INTERVAL_MINUTES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_dashboard.log'),
        logging.StreamHandler()
    ]
)

class WeatherDashboard:
    def __init__(self):
        self.weather_api = WeatherAPI()
        self.display = WeatherDisplay()
        self.last_update = None
        self.update_count = 0
        
        logging.info("Weather Dashboard initialized")
        logging.info(f"Update interval: {UPDATE_INTERVAL_MINUTES} minutes")
    
    def update_weather(self):
        """Fetch weather data and update display"""
        try:
            logging.info("Starting weather update...")
            
            # Fetch weather data
            weather_data = self.weather_api.get_weather_data()
            
            if weather_data and weather_data.get('current'):
                # Update display
                self.display.update_display(weather_data)
                
                self.last_update = datetime.now()
                self.update_count += 1
                
                logging.info(f"Weather update successful (update #{self.update_count})")
                logging.info(f"Current temperature: {weather_data['current']['temperature']}°")
                
            else:
                logging.error("Failed to fetch weather data")
                # Show error on display
                self.display.update_display(None)
                
        except Exception as e:
            logging.error(f"Error during weather update: {e}")
            # Try to show error on display
            try:
                self.display.update_display(None)
            except:
                logging.error("Failed to update display with error message")
    
    def run_initial_update(self):
        """Run initial update immediately"""
        logging.info("Running initial weather update...")
        self.update_weather()
    
    def run_scheduler(self):
        """Run the scheduled updates"""
        # Schedule regular weather updates every 30 minutes
        schedule.every(UPDATE_INTERVAL_MINUTES).minutes.do(self.update_weather)

        # Schedule midnight update to refresh the day
        schedule.every().day.at("00:00").do(self.update_weather)

        logging.info("Scheduler started. Press Ctrl+C to stop.")
        logging.info(f"Weather updates: Every {UPDATE_INTERVAL_MINUTES} minutes")
        logging.info("Midnight refresh: Enabled (00:00 daily)")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logging.info("Weather dashboard stopped by user")
        except Exception as e:
            logging.error(f"Unexpected error in scheduler: {e}")
    
    def run_once(self):
        """Run a single update and exit (useful for testing)"""
        logging.info("Running single weather update...")
        self.update_weather()
        logging.info("Single update completed")

def main():
    """Main function"""
    print("🌤️  Weather Dashboard for Raspberry Pi")
    print("=" * 40)
    
    try:
        dashboard = WeatherDashboard()
        
        # Run initial update
        dashboard.run_initial_update()
        
        # Check if running in test mode
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            print("Running in test mode - single update only")
            dashboard.run_once()
        else:
            # Run scheduled updates
            dashboard.run_scheduler()
            
    except KeyboardInterrupt:
        print("\nWeather dashboard stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
