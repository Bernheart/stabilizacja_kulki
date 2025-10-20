#define TRIGER_PIN 11
#define ECHO_PIN 12
#define ANALOG_READ_IR_LEFT A4
#define DIGITAL_READ_IR_LEFT 7
#define ANALOG_READ_IR_RIGHT A5
#define DIGITAL_READ_IR_RIGHT 8
// defines variables
long duration;
int distance;
void setup() {
  pinMode(TRIGER_PIN, OUTPUT); // Sets the trigPin as an Output
  pinMode(ECHO_PIN, INPUT); // Sets the echoPin as an Input
  Serial.begin(9600); // Starts the serial communication

  pinMode(ANALOG_READ_IR_LEFT, INPUT);
  pinMode(DIGITAL_READ_IR_LEFT, INPUT);
  pinMode(ANALOG_READ_IR_RIGHT, INPUT);
  pinMode(DIGITAL_READ_IR_RIGHT, INPUT);
}
void loop() {
  // Clears the trigPin
  digitalWrite(TRIGER_PIN, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(TRIGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGER_PIN, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(ECHO_PIN, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(distance);

  Serial.print("analog value left: ");
  Serial.print(analogRead(ANALOG_READ_IR_LEFT));
  Serial.print(" right: ");
  Serial.print(analogRead(ANALOG_READ_IR_RIGHT));
  Serial.print(" digital value left: ");
  Serial.print(digitalRead(DIGITAL_READ_IR_LEFT));
  Serial.print(" right: ");
  Serial.println(digitalRead(DIGITAL_READ_IR_RIGHT));
  delay(500);
}