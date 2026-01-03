import time
import socket
import redis
import json

# ===== CONFIG =====
ESP32_IP = "192.168.188.122"
PORT = 4210

CENTER = 160
R = 25
CONTROL_HZ = 2
CONTROL_INTERVAL = 1.0 / CONTROL_HZ

QUEUE_NAME = "fire_centers"
# ==================

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(cmd):
    sock.sendto(cmd.encode(), (ESP32_IP, PORT))
    print("Sent:", cmd)


def main():
    r = redis.Redis()

    last_control_time = 0
    last_pump_time = 0
    is_pumping = False

    while True:
        # BLOCK until data exists
        _, data = r.blpop(QUEUE_NAME)

        payload = json.loads(data)
        centers = payload["centers"]

        now = time.time()

        if not centers:
            continue

        x, y = centers[0]

        if now - last_control_time < CONTROL_INTERVAL:
            continue

        last_control_time = now

        if x < CENTER - R:
            send_cmd("l")
        elif x > CENTER + R:
            send_cmd("r")
        else:
            print("🔥 FIRE CENTERED")
            send_cmd("w")
            last_pump_time = now
            is_pumping = True

        if is_pumping and now - last_pump_time > 3:
            send_cmd("s")
            is_pumping = False


if __name__ == "__main__":
    main()
