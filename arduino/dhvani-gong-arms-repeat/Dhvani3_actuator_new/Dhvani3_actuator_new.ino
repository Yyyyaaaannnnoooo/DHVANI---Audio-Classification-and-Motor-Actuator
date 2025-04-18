/*
Dhvani3 Robotic Arm firmware
Project by Budhadtiya 
Firmware developer : Craftronixlab Technologies  
Version : 3.0
--------------------------------------------------------------------------------------------------
Debug message sequence for one movement cycle:
Started 
SW1
SW2
SW1
Stopped 
done (use it as an ACK signal to chk status of the arm)

Uncomment debug msg lines for debugging otherwise it will only send done msg to raspberry pi's
serial which can be processed in python and send start msg for next cycle.

Message format : startFxBx (x denotes the speed for forward and backward)

For e.g : If user wants to move the arm to forward at the speed of 45 and backward at the speed of 25 the command sent to the serial will be 
          startF45B25
--------------------------------------------------------------------------------------------------
*/

#define lsw1Pin 2
#define lsw2Pin 3
#define motorPWM 6 // Motor external PWM
#define motorDIR 7 // Motor direction control
#define flagPin 9
#define feedbackPin 10
#define testPin A1
#define cycleStatus A0

String initCMD;
int motorCWSpeed = 0;
int motorCCWSpeed = 0;
int repetitions = 1;

void setup() {
  Serial.begin(9600);
  pinMode(lsw1Pin, INPUT);
  pinMode(lsw2Pin, INPUT);
  pinMode(testPin, INPUT);
  pinMode(feedbackPin, INPUT);
  pinMode(motorPWM, OUTPUT);
  pinMode(motorDIR, OUTPUT);
  pinMode(flagPin, OUTPUT);
  pinMode(cycleStatus, OUTPUT);
  digitalWrite(flagPin, HIGH);
  attachInterrupt(digitalPinToInterrupt(lsw1Pin), CW, FALLING);
  attachInterrupt(digitalPinToInterrupt(lsw2Pin), CCW, FALLING);
}

void loop() {
  if (Serial.available()) {
    String initCMD = Serial.readStringUntil('\n');
    if (initCMD.startsWith("start")) {
      parseCommand(initCMD);
      for (int i = 0; i < repetitions; i++) {
        runCycle();
      }
      Serial.println("done");
      digitalWrite(cycleStatus, LOW);
    }
  }
  int readPin = digitalRead(feedbackPin);
  if (readPin == LOW) {
    doHoming();
    digitalWrite(flagPin, HIGH);
  }
}

void parseCommand(String cmd) {
  int fIndex = cmd.indexOf('F');
  int bIndex = cmd.indexOf('B');
  int xIndex = cmd.indexOf('x');

  if (fIndex != -1 && bIndex != -1) {
    motorCWSpeed = cmd.substring(fIndex + 1, bIndex).toInt();
  }
  if (bIndex != -1 && xIndex != -1) {
    motorCCWSpeed = cmd.substring(bIndex + 1, xIndex).toInt();
  }
  if (xIndex != -1) {
    repetitions = cmd.substring(xIndex + 1).toInt();
  }
}

void CW() {
  static unsigned long last_interrupt1_time = 0;
  unsigned long interrupt1_time = millis();
  if (interrupt1_time - last_interrupt1_time > 100) {
    stopMotor();
    digitalWrite(flagPin, LOW);
  }
  last_interrupt1_time = interrupt1_time;
}

void CCW() {
  static unsigned long last_interrupt2_time = 0;
  unsigned long interrupt2_time = millis();
  if (interrupt2_time - last_interrupt2_time > 100) {
    analogWrite(motorPWM, motorCCWSpeed);
    digitalWrite(motorDIR, LOW);
  }
  last_interrupt2_time = interrupt2_time;
}

void runCycle() {
  // Move Forward (CW)
  analogWrite(motorPWM, motorCWSpeed);
  digitalWrite(motorDIR, HIGH);
  while (digitalRead(lsw1Pin) == HIGH); // Wait until SW1 is triggered
  stopMotor();
  delay(25);

  // Move Backward (CCW)
  analogWrite(motorPWM, motorCCWSpeed);
  digitalWrite(motorDIR, LOW);
  while (digitalRead(lsw2Pin) == HIGH); // Wait until SW2 is triggered
  stopMotor();
  delay(50);
}

void stopMotor() {
  digitalWrite(motorPWM, LOW);
  digitalWrite(motorDIR, LOW);
}

void doHoming() {
  analogWrite(motorPWM, motorCWSpeed);
  digitalWrite(motorDIR, HIGH);
  delay(100);
  stopMotor();
  Serial.println("done");
  digitalWrite(cycleStatus, LOW);
}