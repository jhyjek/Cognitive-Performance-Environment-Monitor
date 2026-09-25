"""
Cognitive Performance Environment Monitor
------------------------------------------
Reads eCO2 (CCS811) and ambient noise (MAX4466 via PCF8591 ADC), classifies
the environment as GREEN / YELLOW / RED, drives an RGB LED + buzzer + LCD,
and periodically uploads readings to ThingSpeak.

Team: Abdullah Sahto, Jacob Hyjek, Aidan Jerdee
CS 4432 - Sensors and IoT, University of Minnesota Duluth
"""

import time
import requests
import board
import busio
import smbus2
from adafruit_ccs811 import CCS811
from gpiozero import PWMLED, OutputDevice
from RPLCD.i2c import CharLCD

import config

# --- Hardware handles (populated during init) ---
led_red = None
led_yellow = None
led_green = None
buzzer = None
lcd = None
ccs811 = None
bus = None


def init_hardware():
    """Initialize sensors, display, and outputs. Degrades gracefully on failure."""
    global led_red, led_yellow, led_green, buzzer, lcd, ccs811, bus

    print("Initializing Hardware...")

    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ccs811 = CCS811(i2c)
        bus = smbus2.SMBus(config.PCF8591_BUS)

        try:
            lcd = CharLCD(
                i2c_expander="PCF8574",
                address=config.LCD_ADDRESS,
                port=1,
                cols=config.LCD_COLS,
                rows=config.LCD_ROWS,
                dotsize=8,
            )
            lcd.clear()
            lcd.write_string("System Booting...")
        except Exception as lcd_error:
            print(f"! Warning: LCD failed to init (check address 0x27 vs 0x3f): {lcd_error}")

        print("Booting up CO2 sensor, please wait...")
        start_time = time.time()
        while not ccs811.data_ready:
            if time.time() - start_time > config.SENSOR_INIT_TIMEOUT_SECONDS:
                print("Error: CO2 sensor did not become ready. Check connections.")
                break
            time.sleep(1)

        led_red = PWMLED(config.PIN_RED)
        led_yellow = PWMLED(config.PIN_YELLOW)
        led_green = OutputDevice(config.PIN_GREEN)
        buzzer = OutputDevice(config.PIN_BUZZER, active_high=False, initial_value=False)

        print("Hardware initialized.")

    except Exception as e:
        print(f"HARDWARE ERROR: check connections ({e})")


def set_led_color(status):
    if not led_red:
        return

    led_red.value = 0
    led_yellow.value = 0
    led_green.off()

    if status == "GREEN":
        led_green.on()
    elif status == "YELLOW":
        led_yellow.value = 1.0
    elif status == "RED":
        led_red.value = 1.0


def control_buzzer(turn_on):
    if not buzzer:
        return
    buzzer.on() if turn_on else buzzer.off()


def update_lcd_display(co2, noise, status):
    if not lcd:
        return
    try:
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"C:{int(co2)} N:{int(noise)}   ")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"Stat: {status:<8}")
    except Exception as e:
        print(f"LCD Error: {e}")


def get_co2_reading():
    try:
        if ccs811.eco2 is not None:
            return ccs811.eco2
    except Exception:
        pass
    return 400  # fallback: ambient baseline


def get_noise_reading():
    try:
        bus.write_byte(config.PCF8591_ADDR, 0x40 | config.PCF8591_ANALOG_IN_CHANNEL)
        bus.read_byte(config.PCF8591_ADDR)  # dummy read required by PCF8591
        return bus.read_byte(config.PCF8591_ADDR)
    except Exception:
        return 0


def determine_alert_level(co2, noise_raw):
    if co2 > config.CO2_WARNING or noise_raw > config.NOISE_WARNING:
        return "RED", "POOR: Ventilation or quiet needed!"
    elif co2 > config.CO2_SAFE or noise_raw > config.NOISE_SAFE:
        return "YELLOW", "WARNING: Quality decreasing."
    return "GREEN", "Optimal environment"


def send_to_thingspeak(co2, noise, status_code):
    if not config.THINGSPEAK_API_KEY:
        return  # no key configured, skip upload

    payload = {
        "api_key": config.THINGSPEAK_API_KEY,
        "field1": co2,
        "field2": noise,
        "field3": status_code,
    }
    try:
        requests.get(config.THINGSPEAK_URL, params=payload, timeout=5)
    except requests.RequestException:
        pass


def status_to_graph_code(status):
    return {"GREEN": 1, "YELLOW": 2, "RED": 3}.get(status, 1)


def main():
    init_hardware()

    print("--- Starting Cognitive Performance Environment Monitor ---")
    print("--- Press Ctrl+C to stop ---")

    last_upload_time = 0

    try:
        while True:
            current_co2 = get_co2_reading()
            current_noise = get_noise_reading()

            status, message = determine_alert_level(current_co2, current_noise)
            graph_status = status_to_graph_code(status)

            set_led_color(status)
            update_lcd_display(current_co2, current_noise, status)

            print(f"SENSORS | CO2: {current_co2} ppm | Noise: {current_noise} | Status: {status}")

            now = time.time()
            if now - last_upload_time > config.UPLOAD_INTERVAL_SECONDS:
                send_to_thingspeak(current_co2, current_noise, graph_status)
                last_upload_time = now
                print("Cloud updated!")

            if status == "RED":
                control_buzzer(True)
                time.sleep(0.5)
                control_buzzer(False)
                time.sleep(0.1)
            elif status == "YELLOW":
                control_buzzer(True)
                time.sleep(0.5)
                control_buzzer(False)
            else:
                time.sleep(config.LOOP_DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\nSystem stopping...")
        if lcd:
            lcd.clear()
    finally:
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
