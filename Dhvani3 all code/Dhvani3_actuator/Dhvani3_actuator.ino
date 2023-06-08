/*
Dhvani3 Robotic Arm firmware
Project by Budhadtiya 
Firmware developer : Craftronixlab Technologies  
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
--------------------------------------------------------------------------------------------------
*/

#define lsw1Pin 2
#define lsw2Pin 3
#define motorPWM 6 //Motor external PWM set JP4 to X and JP6 to EXTPWM in the motor driver 
#define motorDIR 7 //Motor direction control 
#define flagPin 8
#define feedbackPin 12

String initCMD;   //Serial data from raspberry pi to start arm movement cycle
int sw1Counter = 0;
int motorCWSpeed = 25; //Motor CW rotation speed range 0 - 255
int motorCCWSpeed = 25; //Motor CCW rotation speed range 0 - 255
 
void setup(){
  Serial.begin(9600);
  pinMode(lsw1Pin,INPUT);
  pinMode(lsw2Pin,INPUT);
  pinMode(feedbackPin,INPUT);
  pinMode(motorPWM,OUTPUT);
  pinMode(motorDIR,OUTPUT);
  pinMode(flagPin,OUTPUT);
  digitalWrite(flagPin,HIGH);
  attachInterrupt(digitalPinToInterrupt(lsw1Pin), CW, CHANGE);
  attachInterrupt(digitalPinToInterrupt(lsw2Pin), CCW, LOW);
}

void loop(){
  if(Serial.available()){
    initCMD = Serial.readStringUntil('\n');
    initCMD.trim();
    if(initCMD.equals("start")){
      //Serial.println("Started");
      runCycle();
    } 
   }
  int readPin = digitalRead(feedbackPin);
  if(readPin == LOW){
    doHoming();
    digitalWrite(flagPin,HIGH);
    }
}

void CW(){
  static unsigned long last_interrupt1_time = 0;
  unsigned long interrupt1_time = millis();
  if(interrupt1_time - last_interrupt1_time > 100){
    //Serial.println("SW1");
    sw1Counter = sw1Counter + 1;
    if(sw1Counter == 1){
      sw1Counter = 0;
      stopMotor();
      digitalWrite(flagPin,LOW);
    }
  }
  last_interrupt1_time = interrupt1_time;
}

void CCW(){
  static unsigned long last_interrupt2_time = 0;
  unsigned long interrupt2_time = millis();
  if(interrupt2_time - last_interrupt2_time > 100){
    //Serial.println("SW2");
    analogWrite(motorPWM,motorCCWSpeed);
    digitalWrite(motorDIR,LOW);
  }
  last_interrupt2_time = interrupt2_time;
}

void stopMotor(){
  digitalWrite(motorPWM,LOW);
  digitalWrite(motorDIR,LOW);
  //Serial.println("Stopped");
}

void runCycle(){
  analogWrite(motorPWM,motorCWSpeed);
  digitalWrite(motorDIR,HIGH);
}

void doHoming(){
  analogWrite(motorPWM,motorCWSpeed);
  digitalWrite(motorDIR,HIGH);
  delay(700);
  stopMotor();
  Serial.println("done");
}
