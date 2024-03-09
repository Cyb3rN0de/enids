#!/usr/bin/env python3
from apa102 import APA102
import RPi.GPIO as GPIO
import os

# Define the file path for storing LED statuses
status_file_path = 'led_statuses.json'

def reset_leds():
    # Initialize the APA102 LED strip
    num_leds = 8
    data_pin = 23
    clock_pin = 24
    brightness = 0.1
    lights = APA102(num_leds, data_pin, clock_pin, brightness=brightness)

    print("Toucan: now turning them all off again")
    for i in range(num_leds):
        lights.set_pixel(i, 0, 0, 0)  # Turn off each LED
    lights.show()

    GPIO.cleanup()

    # Delete the led_statuses.json file if it exists
    if os.path.exists(status_file_path):
        os.remove(status_file_path)
        print("LED status file deleted.")
    else:
        print("LED status file not found, no need to delete.")

if __name__ == "__main__":
    reset_leds()
