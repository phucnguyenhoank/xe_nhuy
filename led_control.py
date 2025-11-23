import requests

ESP32_IP = "192.168.249.205"
url = f"http://{ESP32_IP}"

while True:
    cmd = input("Type 'on' or 'off': ").strip().lower()
    if cmd in ["on", "off"]:
        requests.get(f"{url}/{cmd}")
        print(f"LED turned {cmd.upper()}")
    else:
        print("Invalid command")
