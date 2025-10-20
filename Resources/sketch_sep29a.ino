void setup() {
  Serial.begin(9600); // uruchamiamy port szeregowy z prędkością 9600 bps
  Serial.println("Arduino gotowe do komunikacji!");
  pinMode(13, OUTPUT);
}

void loop() {
  // Odczyt danych z PC
  if (Serial.available() > 0) {
    char data = Serial.read();
    Serial.print("Otrzymano: ");
    Serial.println(data);

    // prosta reakcja – np. włączenie LED na pinie 13
    if (data == '1') {
      digitalWrite(13, HIGH);
      Serial.println("LED ON");
      digitalWrite(13, HIGH);
    }
    else if (data == '0') {
      digitalWrite(13, LOW);
      Serial.println("LED OFF");
      digitalWrite(13, LOW);
    }
  }
}
