#include <AccelStepper.h>

#define DIR  7
#define STEP 8
#define ENPIN 11

AccelStepper charkaStepper(AccelStepper::DRIVER, STEP, DIR);

String initCMD;   //Serial data from raspberry pi to start arm movement cycle

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(ENPIN, OUTPUT);
  digitalWrite(ENPIN, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  runSeq();
  delay(300000);
}

void runSeq(){
  //Serial.println("sequence initiated");
  charkaStepper.setSpeed(100);
  charkaStepper.setAcceleration(5);
  charkaStepper.moveTo(8000); // for how long the sequence will run (60s preset)
  while(charkaStepper.distanceToGo() != 0){
  charkaStepper.run();
  }
  charkaStepper.setCurrentPosition(0);
}
