"""
Configuration for the Cognitive Performance Environment Monitor.
Keep pins, thresholds, and display settings here so monitor.py stays clean.
"""

import os

# --- ThingSpeak (cloud logging) ---
# Set this as an environment variable, never hardcode it.
THINGSPEAK_API_KEY = os.environ.get("THINGSPEAK_API_KEY", "")
THINGSPEAK_URL = "https://api.thingspeak.com/update"
UPLOAD_INTERVAL_SECONDS = 60

# --- GPIO wiring (BCM numbering) ---
PIN_RED = 13
PIN_YELLOW = 12
PIN_GREEN = 26
PIN_BUZZER = 21

# --- Air quality thresholds (eCO2 ppm) ---
CO2_SAFE = 800
CO2_WARNING = 1000

# --- Noise thresholds (raw ADC reading, 0-255) ---
NOISE_SAFE = 130
NOISE_WARNING = 135

# --- LCD (I2C) ---
LCD_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2

# --- Sound sensor via PCF8591 ADC ---
PCF8591_ADDR = 0x48
PCF8591_BUS = 1
PCF8591_ANALOG_IN_CHANNEL = 0

# --- Loop timing ---
SENSOR_INIT_TIMEOUT_SECONDS = 30
LOOP_DELAY_SECONDS = 5
