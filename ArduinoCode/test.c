// used Arduino Uno
#include <Servo.h>
#define LED 2 // Led -> pin2
#define light A0 // light -> pinA0
Servo myServo;

int angle = 0, reg = 0;
char Data = 0;
String temp = "";

void setup(){
    myServo.attch(9); // servo -> pin9
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop(){
    while(Serial.available() > 0){
	Data = Serial.read()
	temp += Data;
    }

    if(temp != ""){
	angle = temp.toInt();
	Serial.println(angle);
	temp = "";
	myServo.write(angle);
    }

    reg = analogRead(light);
    Serial.println(reg);
    analogWrite(LED, 1024 - v);

    delay(100);
}