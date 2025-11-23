#include <Arduino.h>

// Motor A
#define ENA_A 19
#define IN1_A 5
#define IN2_A 18

// Motor B
#define ENA_B 17
#define IN1_B 16
#define IN2_B 4

// Reusable function
void runMotor(int enablePin, int in1Pin, int in2Pin, bool forward) {
  // Set direction
  digitalWrite(in1Pin, forward ? HIGH : LOW);
  digitalWrite(in2Pin, forward ? LOW : HIGH);

  // Full speed
  ledcWrite(enablePin, 255);

  // Run for 500 ms
  delay(500);

  // Stop
  ledcWrite(enablePin, 0);
}

void setup() {
  // Motor A pins
  pinMode(IN1_A, OUTPUT);
  pinMode(IN2_A, OUTPUT);
  ledcAttach(ENA_A, 5000, 8);

  // Motor B pins
  pinMode(IN1_B, OUTPUT);
  pinMode(IN2_B, OUTPUT);
  ledcAttach(ENA_B, 5000, 8);
}

void loop() {
  // Motor A forward
  runMotor(ENA_A, IN1_A, IN2_A, true);
  // Motor B forward
  runMotor(ENA_B, IN1_B, IN2_B, true);

  delay(500);

  // Motor A backward
  runMotor(ENA_A, IN1_A, IN2_A, false);
  // Motor B backward
  runMotor(ENA_B, IN1_B, IN2_B, false);

  delay(500);
}
