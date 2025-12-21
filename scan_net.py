from scapy.all import ARP, Ether, srp

def scan_lan(ip_range):
    # Tạo gói tin ARP request để hỏi "Ai có IP này?"
    arp = ARP(pdst=ip_range)
    # Tạo gói tin Ether broadcast để gửi đến tất cả thiết bị (ff:ff:ff:ff:ff:ff)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Gửi gói tin và nhận phản hồi (timeout 2 giây)
    result = srp(packet, timeout=2, verbose=False)[0]

    # Danh sách kết quả
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    return devices

lan_devices = scan_lan("192.168.28.0/24")
print("IP Address\t\tMAC Address")
for device in lan_devices:
    print(f"{device['ip']}\t\t{device['mac']}")
