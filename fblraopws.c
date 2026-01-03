#include <WiFi.h>
#include <WiFiUdp.h>
#include <Arduino.h>

#define BLYNK_TEMPLATE_ID "TMPL65XJ9crU5"
#define BLYNK_TEMPLATE_NAME "xedaplua"
#define BLYNK_AUTH_TOKEN "sEguop21m_lHTNLNdMVhq5MLoCJXQIAP"

#include <BlynkSimpleEsp32.h>

// Motor A
#define ENA_A 22
#define IN1_A 16
#define IN2_A 17

// Motor B
#define ENA_B 23
#define IN1_B 18
#define IN2_B 19

// Alert (buzzer / LED)
#define ALERT_PIN 5

// Pump
#define PUMP_PIN 25

// Wi-Fi credentials
const char* ssid     = "pcas";
const char* password = "pasdpasd";

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
    case 'l': // left (A forward, B backward)
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    case 'r': // right (A backward, B forward)
      runMotor(ENA_A, IN1_A, IN2_A, false);
      runMotor(ENA_B, IN1_B, IN2_B, true);
      break;
    default:
      stopMotor(ENA_A);
      stopMotor(ENA_B);
      return;
  }

  delay(100);
  stopMotor(ENA_A);
  stopMotor(ENA_B);
}

// ------------------- Alert -------------------
void alertOn() {
  digitalWrite(ALERT_PIN, HIGH);
}

void alertOff() {
  digitalWrite(ALERT_PIN, LOW);
}

// ------------------- Alert -------------------
void pumpOn() {
  digitalWrite(PUMP_PIN, HIGH);
}

void pumpOff() {
  digitalWrite(PUMP_PIN, LOW);
}


// Cloud Alert
void sendAlert(String message) {
  // "my_alert" MUST match the "Event Code" in Blynk Console
  Blynk.logEvent("fire_alert", message); 
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

  // Alert
  pinMode(ALERT_PIN, OUTPUT);
  digitalWrite(ALERT_PIN, LOW); // alert OFF by default

  // Pump
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW); // NO pump/HIGH by default

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

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);
  Serial.println("Blynk began.");
}

// ------------------- Loop -------------------
void loop() {
  Blynk.run();

  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buf[10];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len > 0) buf[len] = 0;  // null terminate
    Serial.print("Received: ");
    Serial.println(buf);

    char cmd = buf[0];  // first character only
    switch (cmd) {
      case 'a':   // alert ON
        alertOn();
        Serial.println("Alert ON");
        break;

      case 'o':   // alert OFF
        alertOff();
        Serial.println("Alert OFF");
        break;
      
      case 'p':   // send cloud alert, p means phone
        sendAlert("FIRE IN YOUR HOUSE!");
        Serial.println("FIRE IN YOUR HOUSE!");
        break;
      
      case 'w':   // water, PUMP
        Serial.println("Pump...");
        pumpOn();
        Serial.println("Pump water");
        break;
      
      case 's':   // stop pumping water, PUMP
        pumpOff();
        Serial.println("Stop Pump");
        break;

      default:    // motor commands
        move(cmd);
        break;
    }
  }

  delay(1); // yield to watchdog
}
