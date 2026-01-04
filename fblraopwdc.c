#include <WiFi.h>
#include <WiFiUdp.h>
#include <Arduino.h>

// --- BLYNK CONFIG ---
#define BLYNK_TEMPLATE_ID   "TMPL65XJ9crU5"
#define BLYNK_TEMPLATE_NAME "xedaplua"
#define BLYNK_AUTH_TOKEN    "sEguop21m_lHTNLNdMVhq5MLoCJXQIAP"
#include <BlynkSimpleEsp32.h>

// --- PIN DEFINITIONS ---
// Motor A
#define ENA_A 22
#define IN1_A 16
#define IN2_A 17

// Motor B
#define ENA_B 23
#define IN1_B 18
#define IN2_B 19

// Peripherals
#define ALERT_PIN 5
#define PUMP_PIN  25
#define TRIG_PIN  27
#define ECHO_PIN  26

// --- NETWORK CONFIG ---
const char* ssid     = "pcas";
const char* password = "pasdpasd";
unsigned int localPort = 4210;
WiFiUDP udp;

// --- STATE MANAGEMENT ---
bool isAutoMode = false; // Mặc định là FALSE (không tự chạy)

// ================= MOTOR FUNCTIONS =================
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
    case 'f': // Tiến
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, true);
      break;
    case 'b': // Lùi
      runMotor(ENA_A, IN1_A, IN2_A, false);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    case 'l': // Trái
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    case 'r': // Phải
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

// ================= PERIPHERAL FUNCTIONS =================
void alertOn() {
  digitalWrite(ALERT_PIN, HIGH);
}

void alertOff() {
  digitalWrite(ALERT_PIN, LOW);
}

void pumpWater() {
  digitalWrite(PUMP_PIN, HIGH);
  delay(1000);
  digitalWrite(PUMP_PIN, LOW);
}

void sendAlert(String message) {
  Blynk.logEvent("fire_alert", message);
}

// ================= SENSOR & LOGIC =================
long readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout 30ms
  if (duration == 0) return -1;

  long distance = duration * 0.034 / 2;
  return distance;
}

void autoExplore() {
  long dist = readDistanceCM();
  Serial.print("Auto Mode - Dist: ");
  Serial.println(dist);

  if (dist < 0) {
    move('f'); // Lỗi cảm biến -> cứ đi thẳng
    return;
  }

  if (dist < 25) {
    // Gặp vật cản
    move('b'); 
    int r = random(0, 100);
    char turnCmd = (r < 70) ? 'l' : 'r';
    for(int i = 0; i < 5; i++) {
      move(turnCmd);
    }
  } else {
    move('f'); // Đường thoáng
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);

  // Cấu hình Motor
  pinMode(IN1_A, OUTPUT); pinMode(IN2_A, OUTPUT);
  pinMode(IN1_B, OUTPUT); pinMode(IN2_B, OUTPUT);
  ledcAttach(ENA_A, 5000, 8);
  ledcAttach(ENA_B, 5000, 8);

  // Cấu hình Peripherals
  pinMode(ALERT_PIN, OUTPUT); digitalWrite(ALERT_PIN, LOW);
  pinMode(PUMP_PIN, OUTPUT);  digitalWrite(PUMP_PIN, LOW);
  pinMode(TRIG_PIN, OUTPUT);  pinMode(ECHO_PIN, INPUT);

  // Kết nối Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected! IP: " + WiFi.localIP().toString());

  udp.begin(localPort);
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);
  Serial.println("System Ready. Waiting for commands...");
}

// ================= LOOP =================
void loop() {
  Blynk.run();

  // Chỉ chạy Auto Explore nếu biến cờ (flag) được bật
  if (isAutoMode) {
    autoExplore();
  }

  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buf[10];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len > 0) buf[len] = 0;
    
    Serial.print("Received: ");
    Serial.println(buf);

    char cmd = buf[0];
    switch (cmd) {
      case 'd': // Bật chế độ tự lái (Drive/Auto)
        isAutoMode = true;
        Serial.println(">>> AUTO MODE: ON");
        break;

      case 'c': // Tắt chế độ tự lái (Cancel/Control)
        isAutoMode = false;
        // Đảm bảo dừng xe ngay lập tức khi tắt auto
        stopMotor(ENA_A);
        stopMotor(ENA_B);
        Serial.println(">>> AUTO MODE: OFF");
        break;

      case 'a': alertOn();  Serial.println("Alert ON"); break;
      case 'o': alertOff(); Serial.println("Alert OFF"); break;
      case 'p': sendAlert("FIRE IN YOUR HOUSE!"); Serial.println("FIRE SENT"); break;
      case 'w': pumpWater(); Serial.println("Pump Active"); break;
      
      default:  
        // Các lệnh di chuyển thủ công (f, b, l, r) vẫn hoạt động
        move(cmd); 
        break;
    }
  }
  delay(1);
}