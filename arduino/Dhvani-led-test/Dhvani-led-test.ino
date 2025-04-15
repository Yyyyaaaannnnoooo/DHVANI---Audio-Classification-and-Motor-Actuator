/*
Dhvani3 Robotic Arm firmware
Project by Budhadtiya 
Firmware developer : Craftronixlab Technologies  
Version : 2.0
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
#define motorPWM 6  //Motor external PWM set JP4 to X and JP6 to EXTPWM in the motor driver
#define motorDIR 7  //Motor direction control
#define flagPin 9
#define feedbackPin 10
#define testPin A1
#define cycleStatus A0

String initCMD;  //Serial data from raspberry pi to start arm movement cycle
int sw1Counter = 0;
int motorCWSpeed = 200;   //motor CW speed range 0 - 255
int motorCCWSpeed;  //motor CCW speed range 0 - 255

int blink_counter = 0;
bool should_i_blink = false;

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
  Serial.println("Connected to arduino sketch");

  // LED STUFF
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // if(initCMD.equals("start"))
  if (Serial.available()) {
    String initCMD = Serial.readStringUntil('\n');
    Serial.println(initCMD);
    motorCWSpeed = initCMD.substring(6, 8).toInt();
    Serial.println(motorCWSpeed);
    motorCCWSpeed = initCMD.substring(9, 12).toInt();
    Serial.println(motorCCWSpeed);
    if (initCMD.substring(0, 5) == "start") {
      Serial.println("Started");
      // should_i_blink = true;
      
      // runCycle();
      // digitalWrite(cycleStatus, HIGH);
    }
  }
  blink(motorCWSpeed);
  // int readPin = digitalRead(feedbackPin);
  // if(readPin == LOW){
  //   doHoming();
  //   digitalWrite(flagPin,HIGH);
  //   }
}

void blink(int value) {
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(value * 10);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(value * 10);
}

void CW() {
  static unsigned long last_interrupt1_time = 0;
  unsigned long interrupt1_time = millis();
  if (interrupt1_time - last_interrupt1_time > 100) {
    //Serial.println("SW1");
    sw1Counter = sw1Counter + 1;
    if (sw1Counter == 1) {
      sw1Counter = 0;
      stopMotor();
      digitalWrite(flagPin, LOW);
    }
  }
  last_interrupt1_time = interrupt1_time;
}

void CCW() {
  static unsigned long last_interrupt2_time = 0;
  unsigned long interrupt2_time = millis();
  if (interrupt2_time - last_interrupt2_time > 100) {
    //Serial.println("SW2");
    analogWrite(motorPWM, motorCCWSpeed);
    digitalWrite(motorDIR, LOW);
  }
  last_interrupt2_time = interrupt2_time;
}

void stopMotor() {
  digitalWrite(motorPWM, LOW);
  digitalWrite(motorDIR, LOW);
  //Serial.println("Stopped");
}

void runCycle() {
  analogWrite(motorPWM, motorCWSpeed);
  digitalWrite(motorDIR, HIGH);
}

void doHoming() {
  analogWrite(motorPWM, motorCWSpeed);
  digitalWrite(motorDIR, HIGH);
  delay(100);
  stopMotor();
  Serial.println("done");
  digitalWrite(cycleStatus, LOW);
}
