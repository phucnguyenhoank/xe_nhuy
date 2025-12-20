import socket

ESP32_IP = "192.168.138.122"  # replace with your ESP32 IP
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Commands: f=forward, b=backward, l=left, r=right, q=quit, a=alert, o=off_alert")
while True:
    cmd = input("Enter command: ").strip().lower()
    if cmd == "q":
        break
    elif cmd in ["f", "b", "l", "r", "a", "o"]:
        sock.sendto(cmd.encode(), (ESP32_IP, PORT))
        print(f"Sent {cmd}")
    else:
        print("Invalid command")
