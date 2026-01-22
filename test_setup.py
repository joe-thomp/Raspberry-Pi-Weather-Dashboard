#!/usr/bin/env python3
"""
Test script to verify the weather dashboard setup
Run this to check if everything is configured correctly
"""

import sys
import os
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✅ requests module available")
    except ImportError:
        print("❌ requests module not found - run: pip3 install requests")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ PIL (Pillow) module available")
    except ImportError:
        print("❌ PIL module not found - run: pip3 install Pillow")
        return False
    
    try:
        from inky.auto import auto
        print("✅ inky module available")
    except ImportError:
        print("❌ inky module not found - run: pip3 install inky[impression]")
        return False
    
    try:
        import schedule
        print("✅ schedule module available")
    except ImportError:
        print("❌ schedule module not found - run: pip3 install schedule")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv module available")
    except ImportError:
        print("❌ python-dotenv module not found - run: pip3 install python-dotenv")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import OPENWEATHER_API_KEY, CITY_NAME, COUNTRY_CODE, UNITS
        print(f"✅ Configuration loaded")
        print(f"   City: {CITY_NAME}, {COUNTRY_CODE}")
        print(f"   Units: {UNITS}")
        
        if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'your_api_key_here':
            print("❌ OpenWeatherMap API key not configured")
            print("   Please edit .env file and add your API key")
            return False
        else:
            print("✅ API key configured")
            return True
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_weather_api():
    """Test weather API connection"""
    print("\nTesting weather API...")
    
    try:
        from weather_api import WeatherAPI
        weather = WeatherAPI()
        
        print("Fetching current weather...")
        current = weather.get_current_weather()
        
        if current:
            print("✅ Weather API working")
            print(f"   Temperature: {current['temperature']}°")
            print(f"   Description: {current['description']}")
            print(f"   City: {current['city']}")
            return True
        else:
            print("❌ Failed to fetch weather data")
            return False
            
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

def test_display():
    """Test display functionality"""
    print("\nTesting display...")
    
    try:
        from weather_display import WeatherDisplay
        display = WeatherDisplay()
        print("✅ Display initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Display error: {e}")
        print("   Make sure your Inky Impression is properly connected")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'weather_dashboard.py',
        'weather_api.py',
        'weather_display.py',
        'config.py',
        'requirements.txt',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🌤️  Weather Dashboard Setup Test")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Weather API", test_weather_api),
        ("Display", test_display)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("TEST RESULTS")
    print("=" * 40)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your weather dashboard is ready to go.")
        print("\nTo start the dashboard:")
        print("  python3 weather_dashboard.py --test  # Test run")
        print("  python3 weather_dashboard.py         # Continuous mode")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the dashboard.")
        print("\nCommon fixes:")
        print("  1. Install missing dependencies: pip3 install -r requirements.txt")
        print("  2. Configure API key in .env file")
        print("  3. Check Inky Impression connection")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
