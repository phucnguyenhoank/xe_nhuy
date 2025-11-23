#include <WiFi.h>
#include <WiFiUdp.h>
#include <Arduino.h>

// Motor A
#define ENA_A 19
#define IN1_A 5
#define IN2_A 18

// Motor B
#define ENA_B 17
#define IN1_B 16
#define IN2_B 4

// Wi-Fi credentials
const char* ssid     = "pcas";
const char* password = "phucansangdi";

WiFiUDP udp;
unsigned int localPort = 4210;  // UDP port

// ------------------- Motor functions -------------------
void runMotor(int enablePin, int in1Pin, int in2Pin, bool forward) {
  digitalWrite(in1Pin, forward ? HIGH : LOW);
  digitalWrite(in2Pin, forward ? LOW : HIGH);
  ledcWrite(enablePin, 255);
}

void stopMotor(int enablePin) {
  ledcWrite(enablePin, 0);
}

void move(char cmd) {
  switch (cmd) {
    case 'f': // forward
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, true);
      break;
    case 'b': // backward
      runMotor(ENA_A, IN1_A, IN2_A, false);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    case 'l': // left (A backward, B forward)
      runMotor(ENA_A, IN1_A, IN2_A, false);
      runMotor(ENA_B, IN1_B, IN2_B, true);
      break;
    case 'r': // right (A forward, B backward)
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    default:
      stopMotor(ENA_A);
      stopMotor(ENA_B);
      return;
  }

  delay(500); // run for 500ms
  stopMotor(ENA_A);
  stopMotor(ENA_B);
}

// ------------------- Setup -------------------
void setup() {
  Serial.begin(115200);

  // Motor A pins
  pinMode(IN1_A, OUTPUT);
  pinMode(IN2_A, OUTPUT);
  ledcAttach(ENA_A, 5000, 8);

  // Motor B pins
  pinMode(IN1_B, OUTPUT);
  pinMode(IN2_B, OUTPUT);
  ledcAttach(ENA_B, 5000, 8);

  // Wi-Fi connect
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

// ------------------- Loop -------------------
void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buf[10];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len > 0) buf[len] = 0;  // null terminate
    Serial.print("Received: ");
    Serial.println(buf);

    char cmd = buf[0];  // first character only
    move(cmd);
  }

  delay(1); // yield to watchdog
}
