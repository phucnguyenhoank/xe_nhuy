#define LED_PIN 2  // Safe built-in LED on most ESP32 boards

void setup() {
  pinMode(LED_PIN, OUTPUT);  // Set LED pin as output
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // Turn LED ON
  delay(100);
  digitalWrite(LED_PIN, LOW);   // Turn LED OFF
  delay(100);
}
