#define BLYNK_TEMPLATE_ID           "TMPL6T-kiIZuC"
#define BLYNK_TEMPLATE_NAME         "Quickstart Template"
#define BLYNK_AUTH_TOKEN            "jpMFUHeER7UdaLx2kxqmpUoIWX8JX6Ed"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

char ssid[] = "pcas";
char pass[] = "pasdpasd";

// A simple reusable function for alerts
void sendAlert(String message) {
  // "my_alert" MUST match the "Event Code" in Blynk Console
  Blynk.logEvent("fire_alert", message); 
}

// Triggered when you press a button on Virtual Pin 0 in the app
BLYNK_WRITE(V0) {
  if (param.asInt() == 1) { 
    sendAlert("FIRE IN YOUR HOUSE"); 
  }
}

void setup() {
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}

void loop() {
  Blynk.run();
}
