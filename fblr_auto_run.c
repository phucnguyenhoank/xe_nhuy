#include <Arduino.h>

// Motor A
#define ENA_A 19
#define IN1_A 5
#define IN2_A 18

// Motor B
#define ENA_B 17
#define IN1_B 16
#define IN2_B 4

// Run a single motor
void runMotor(int enablePin, int in1Pin, int in2Pin, bool forward) {
  digitalWrite(in1Pin, forward ? HIGH : LOW);
  digitalWrite(in2Pin, forward ? LOW : HIGH);
  ledcWrite(enablePin, 255);  // full speed
}

// Stop a single motor
void stopMotor(int enablePin) {
  ledcWrite(enablePin, 0);
}

// Move function for both motors
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
    case 'l': // turn left (A backward, B forward)
      runMotor(ENA_A, IN1_A, IN2_A, false);
      runMotor(ENA_B, IN1_B, IN2_B, true);
      break;
    case 'r': // turn right (A forward, B backward)
      runMotor(ENA_A, IN1_A, IN2_A, true);
      runMotor(ENA_B, IN1_B, IN2_B, false);
      break;
    default:
      // invalid command, stop both
      stopMotor(ENA_A);
      stopMotor(ENA_B);
      return;
  }

  delay(500);  // run for 500ms

  // stop motors
  stopMotor(ENA_A);
  stopMotor(ENA_B);
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
  // Example usage:
  move('f'); // forward
  delay(500);
  move('b'); // backward
  delay(500);
  move('l'); // left
  delay(500);
  move('r'); // right
  delay(500);
}
