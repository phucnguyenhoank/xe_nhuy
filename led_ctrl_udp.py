import socket

ESP32_IP = "192.168.249.205"  # your ESP32 IP
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    cmd = input("Command (on/off/quit): ").strip().lower()
    if cmd == "quit":
        break
    elif cmd in ["on", "off"]:
        sock.sendto(cmd.encode(), (ESP32_IP, PORT))
        print(f"Sent {cmd}")
    else:
        print("Invalid command")
