#!/usr/bin/env python3
from apa102 import APA102
import RPi.GPIO as GPIO
import sys
import json

# Define the file path for storing LED statuses
status_file_path = 'led_statuses.json'

# Initialize the APA102 LED strip
num_leds = 8
data_pin = 23
clock_pin = 24
brightness = 0.1
lights = APA102(num_leds, data_pin, clock_pin, brightness=brightness)

def load_led_statuses():
    """Load LED statuses from a file, or initialize if the file does not exist."""
    try:
        with open(status_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Initialize all LEDs to OFF (0) if the file does not exist
        return [0] * num_leds

def save_led_statuses(statuses):
    """Save LED statuses to a file."""
    with open(status_file_path, 'w') as file:
        json.dump(statuses, file)

def set_light_by_protocol(protocol, status):
    """Set the LED light by protocol, updating both the LED strip and the status file."""
    protocol_to_led = {
        'ftp': 0,
        'ssh': 1,
        'http': 2,
        'https': 3,
        'snmp': 4,
        'mysql': 5,
	'rdp': 6,
	'git': 7,
    }

    led_index = protocol_to_led.get(protocol.lower())
    if led_index is not None:
        led_statuses = load_led_statuses()
        led_statuses[led_index] = status
        save_led_statuses(led_statuses)

        for index, status in enumerate(led_statuses):
            if status == 1:
                lights.set_pixel(index, 255, 0, 0)  # Turn LED to RED
            else:
                lights.set_pixel(index, 0, 0, 0)  # Turn LED OFF
        lights.show()
    else:
        print(f"No LED configuration for protocol: {protocol}")

def main():
    try:
        if len(sys.argv) != 3:
            print("Usage: ./code.py <protocol> <status>")
            sys.exit(1)

        protocol = sys.argv[1]
        status = int(sys.argv[2])
        set_light_by_protocol(protocol, status)

    except Exception as e:
        print("Error:", e)

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
