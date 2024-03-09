#raspberrypi #pi #python3 #opencanary #toucan  #systemd  #service



> ENIDS = Early Network Intrusion Detection System



![[Pasted image 20240308220517.png]]
>  Raspberry Pi 3 + Toucan LED bar — Having detected SSH, RDP and HTTPS scans



## Context

Using a spare Raspberry Pi, I want to create a canary to flash red lights when services are queried. Since this Pi is not running anything else, there is no reason for those to be triggered during normal activity.

With `opencanary` and a bit of python, we can easily scan the logs for suspicious activity and turn LEDs to red when something is picked up!


## 1. Installing the Toucan
[Vendor](https://littlebirdelectronics.com.au/products/little-bird-toucan-8-x-apa102-rgb-led)    [GitHub](https://github.com/cheshrkat/toucan8)

1. Install the Toucan on your Raspberry Pi's GPIOs (check vendor site to make sure you install it the right way) - tip here is to have the rounded sides toward the outside of the raspberry pi as on the above picture.

2. Clone the repository and play with existing python scripts.

```
ls
	toucan-bluepulse.py
	toucan-fade.py
	toucan-helloworld.py
	toucan-off.py
	toucan.py
	toucan-brightfade.py
	toucan-green.py
	toucan_helpers.py
	toucan-orange.py
	toucan-red.py
```



## 2. Control LEDs for each service

Based on the code snippets provided in the `toucan8` repo, create `toucan-update.py` to match LEDs with services monitored by `opencanary` and control their status (Off or On = Red).

```python
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
```

Usage:

```sh
./toucan-update.py ssh 1     # LED 1 turns red

./toucan-update.py mysql 1     # LED 5 turns red

./toucan-update.py ssh 0     # LED 1 switches off
```


LEDs remain on until another command is provided. Their status is saved in `led_statuses.json`.

```sh
cat led_statuses.json 
	[0, 0, 0, 0, 0, 1, 0, 0]
```




## 3. Reset all LEDs

Now let's create `toucan-reset.py` to reset / switch off all LEDs.

```python
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

    print("Toucan: now turning them all off again")> ENIDS = Early Network Intrusion Detection System
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
```


## 4. Install OpenCanary

[GitHub](https://github.com/thinkst/opencanary)

Clone the repo and install `opencanary`:

```sh
sudo apt-get install python3-dev python3-pip python3-virtualenv python3-venv python3-scapy libssl-dev libpcap-dev

virtualenv env/

. env/bin/activate            < remove (env) with 'deactivate'

pip install opencanary
```

- Optional

```sh
# if you plan to use the Windows File Share module
sudo apt install samba 

# if you plan to use the SNMP module
pip install scapy pcapy-ng 
```

- 1st configuration

```sh
opencanaryd --copyconfig
[*] A sample config file is ready /etc/opencanaryd/opencanary.conf

[*] Edit your configuration, then launch with "opencanaryd --start"
```

Make sure the following services are active:

| Service | Port |
| ------- | ---- |
| ftp     | 21   |
| ssh     | 22   |
| http    | 80   |
| https   | 443  |
| snmp    | 161  |
| mysql   | 3306 |
| rdp     | 3389 |
| git     | 9418 |

- Note

`. env/bin/activate` so that `opencanary` installs its dependencies in a virtual python environment `env` in `/home/pi/Repos/opencanary/env/lib/python3.9/`, avoiding cluttering of the main code base located in `/usr/lib/python3.9/`.

- Further configurations:

Configure `.opencanary.conf` using the text editor of your choice:

```sh
nano .opencanary.conf
	...
	"git.enabled": true,
	...
	"ftp.enabled": true,
	...
	"http.enabled": true,
	...
	"https.enabled": true,
	...
	"portscan.enabled": true,
	...
	"mysql.enabled": true,
	...
	"rdp.enabled": true,
	...
	"snmp.enabled": true,
	...
```

- Tests

A good way to check if `opencanary` is working correctly is by watching the logs while running an nmap scan on localhost or from another device.

- On Raspberry Pi

```sh
tail -f /var/tmp/opencanary.log
```

- On other device

```sh
nmap <Pi IP address>
```





## 5. Scan OpenCanary logs

Now we are ready for the last python script `canary-check.py` that will scan the `opencanary` logs for accessed / compromised services and switch on matching LEDs. By default, those logs are located in `/var/tmp/opencanary.log`.

```python
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
```




## 6. Testing

- On Raspberry Pi:

```sh
./canary-check.py 
Activity detected on port 22 (ssh). Turning LED on.
Activity detected on port 21 (ftp). Turning LED on.
Activity detected on port 3306 (mysql). Turning LED on.
Activity detected on port 3306 (mysql). Turning LED on.
Activity detected on port 3389 (rdp). Turning LED on.
Activity detected on port 80 (http). Turning LED on.
^C
CTRL+C detected! Resetting LEDs and exiting...
Toucan: now turning them all off again
LED status file deleted.
```


- On other device

```sh
nmap 10.82.1.3 -Pn -p 22
PORT   STATE SERVICE
22/tcp open  ssh

nmap 10.82.1.3 -Pn -p 21
PORT   STATE SERVICE
21/tcp open  ftp

nmap 10.82.1.3 -Pn -p 3306
PORT     STATE    SERVICE
3306/tcp filtered mysql

nmap 10.82.1.3 -Pn -p 3389
PORT     STATE SERVICE
3389/tcp open  ms-wbt-server

nmap 10.82.1.3 -Pn -p 80  
PORT   STATE SERVICE
80/tcp open  http
```

The use of `-Pn` is to prevent `nmap` from scanning ports `80` and `443` each time round.



## 7. Turn script into service

- Create service file

```sh
sudo nano /etc/systemd/system/enids.service
```


- Contents

```
[Unit]
Description=Early Network Intrusion Detection System
After=multi-user.target

[Service]
Type=simple
User=matt
WorkingDirectory=/home/matt
ExecStart=/usr/bin/python3 /home/matt/Code/enids/canary-check.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```


- Restart systemctl

```sh
sudo systemctl daemon-reload
```


- Activate and Enable (start at boot) service

```sh
sudo systemctl start enids

sudo systemctl enable enids

sudo systemctl status enids
```

That's it! You may now disconnect (SSH session) from the Raspberry Pi and this script be active even if the Pi temporarily looses power.


![alt text](https://github.com/Cyb3rN0de/enids/blob/main/images/Canary.png?raw=true)
>  Network canary (Source Dall-E)
