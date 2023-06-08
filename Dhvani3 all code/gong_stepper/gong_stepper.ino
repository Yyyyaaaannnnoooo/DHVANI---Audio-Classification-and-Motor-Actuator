#include <AccelStepper.h>

#define DIR  7
#define STEP 8
#define ENPIN 11
#define relayPin 5
#define lswPin 2
#define flagPin 6
#define feedbackPin 9

AccelStepper gongStepper(AccelStepper::DRIVER, STEP, DIR);
String initCMD;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(ENPIN, OUTPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(flagPin, OUTPUT);
  pinMode(feedbackPin, INPUT);
  digitalWrite(flagPin, LOW);
  digitalWrite(relayPin, LOW);
  digitalWrite(ENPIN, LOW);
  attachInterrupt(digitalPinToInterrupt(lswPin), sw_hit, LOW);
}

void loop(){
  // put your main code here, to run repeatedly:
  int readPin = digitalRead(feedbackPin);
  if(readPin == HIGH){
    delay(1000);
    digitalWrite(relayPin, LOW);
    }
    if(Serial.available()){
    initCMD = Serial.readStringUntil('\n');
    initCMD.trim();
    if(initCMD.equals("start")){
      //Serial.println("Started");
      gongSeq();
    } 
  }
}

void sw_hit(){
  //Serial.println("hit");
  digitalWrite(relayPin, HIGH);
  digitalWrite(flagPin, HIGH);
  }

void gongSeq(){
  //Serial.println("gong initiated");
  gongStepper.setSpeed(200);  //gong motor speed 
  gongStepper.setAcceleration(20); //gong motor acceleration
  gongStepper.moveTo(-2000); // gong motor position (for how long the sequence will run)
  while(gongStepper.distanceToGo() != 0){
  gongStepper.run();
  }
  gongStepper.setCurrentPosition(0);
}
