#include <WiFi.h>

// Wi-Fi credentials
const char* ssid = "pcas";
const char* password = "phucansangdi";

WiFiServer server(80);   // HTTP server on port 80

#define LED_PIN 2  // GPIO2 safe LED pin

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // start OFF

  // Connect Wi-Fi
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (!client) return;

  while (!client.available()) delay(1);
  String req = client.readStringUntil('\r');
  client.flush();
  Serial.println(req);

  // Turn LED ON/OFF
  if (req.indexOf("/on") != -1) {
    digitalWrite(LED_PIN, HIGH);
  }
  else if (req.indexOf("/off") != -1) {
    digitalWrite(LED_PIN, LOW);
  }

  // Simple response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/plain\n");
  client.println("OK");
}
