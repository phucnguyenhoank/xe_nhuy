#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid     = "pcas";
const char* password = "phucansangdi";

#define LED_PIN 2      // GPIO2, built-in LED

WiFiUDP udp;
unsigned int localPort = 4210;  // UDP port to listen

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Connect Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  udp.begin(localPort);
  Serial.println("UDP listening on port 4210...");
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buf[20];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len > 0) buf[len] = 0;  // null terminate
    Serial.print("Received: ");
    Serial.println(buf);

    if (strcmp(buf, "on") == 0) {
      digitalWrite(LED_PIN, HIGH);
    } 
    else if (strcmp(buf, "off") == 0) {
      digitalWrite(LED_PIN, LOW);
    }
  }
  delay(1);  // yield to watchdog
}
