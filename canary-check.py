#!/usr/bin/env python3
import tailer
import subprocess
import json
import signal

# Path to the OpenCanary log file
log_file_path = '/var/tmp/opencanary.log'

# Mapping port numbers to protocols
port_to_protocol = {
    '21': 'ftp',
    '22': 'ssh',
    '80': 'http',
    '443': 'https',
    '161': 'snmp',
    '3306': 'mysql',
    '3389': 'rdp',
    '9418': 'git',
    # Add more mappings as necessary
}

def process_log_line(line):
    try:
        log_entry = json.loads(line)
        dst_port = str(log_entry.get('dst_port'))
        protocol = port_to_protocol.get(dst_port)
        if protocol:
            print(f"Activity detected on port {dst_port} ({protocol}). Turning LED on.")
            subprocess.run(['./toucan-update.py', protocol, '1'], check=True)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from log line: {line}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def reset_leds_on_interrupt(signal, frame):
    print("\nCTRL+C detected! Resetting LEDs and exiting...")
    subprocess.run(['./toucan-reset.py'], check=True)
    exit(0)

def follow_log():
    for line in tailer.follow(open(log_file_path)):
        process_log_line(line)

if __name__ == "__main__":
    # Set the signal handler for SIGINT
    signal.signal(signal.SIGINT, reset_leds_on_interrupt)
    follow_log()
