#define GONG_PIN 5         // D5 pin connected to the MOSFET gate

void setup() {
  pinMode(GONG_PIN, OUTPUT);
  digitalWrite(GONG_PIN, LOW);   // Ensure it's off initially
  Serial.begin(9600);
}

void loop() {
  static String inputString = "";

  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;

    if (inChar == '\n' || inputString.length() >= 20) {
      inputString.trim();  // Remove whitespace

      if (inputString.startsWith("hitgongx")) {
        int repeatCount = inputString.substring(8).toInt();  // Get number after "hitgongx"
        
        if (repeatCount > 0 && repeatCount <= 20) {  // Prevent crazy values
          for (int i = 0; i < repeatCount; i++) {
            digitalWrite(GONG_PIN, HIGH);
            delay(100);  // Gong ON
            digitalWrite(GONG_PIN, LOW);
            delay(100);  // Pause between hits
          }
          Serial.println("hit");
        } else {
          Serial.println("invalid repeat count");
        }
      }

      inputString = ""; // Reset for next command
    }
  }
}
