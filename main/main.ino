#include <Arduino.h>

// ======================== KONFIGURACJA =========================
int LEFT_MOTOR_PIN = 9;
int rightMotorPin = 10;
int sonarPin = A0;
int irPin = A1;

int forwardDir = 1;   // 1 = przód, -1 = tył
int rotationDir = 1;  // 1 = prawo, -1 = lewo

int currentSpeed = 150;  // domyślna prędkość (0–255)
// ===============================================================

void setup() {
  Serial.begin(9600);
  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(rightMotorPin, OUTPUT);
  pinMode(sonarPin, INPUT);
  pinMode(irPin, INPUT);
  Serial.println("<READY>");
}

void loop() {
  if (Serial.available()) {
    String frame = Serial.readStringUntil('>');
    if (frame.startsWith("<")) {
      frame.remove(0, 1); // usuń '<'
      handleFrame(frame);
    }
  }
}

// ======================== PARSER =========================
void handleFrame(String frame) {
  int sep1 = frame.indexOf('|');
  int sep2 = frame.lastIndexOf('|');

  if (sep1 == -1 || sep2 == -1 || sep2 <= sep1) {
    Serial.println("<NACK|BAD_FORMAT>");
    return;
  }

  String cmd = frame.substring(0, sep1);
  String param = frame.substring(sep1 + 1, sep2);
  String checksum = frame.substring(sep2 + 1);

  if (!validateChecksum(frame, checksum)) {
    Serial.println("<NACK|" + cmd + "|CHK_ERR>");
    return;
  }

  // Obsługa komend
  char c = cmd.charAt(0);
  switch (c) {
    case 'M': moveRobot(param.toInt()); break;
    case 'R': rotateRobot(param.toInt()); break;
    case 'S': stopRobot(); break;
    case 'V': setSpeed(param.toInt()); break;
    case 'B': readSonar(); break;
    case 'I': readIR(); break;
    case 'C': configureRobot(param); break; // konfiguracja pinów/kierunków
    default:
      Serial.println("<NACK|" + cmd + "|UNKNOWN_CMD>");
      return;
  }

  Serial.println("<ACK|" + cmd + ">");
}

// ===================== WALIDACJA SUMY KONTROLNEJ =====================
// Checksum: suma ASCII znaków przedostatniego '|' modulo 256
bool validateChecksum(String frame, String given) {
  int sep2 = frame.lastIndexOf('|');
  if (sep2 == -1) return false;
  String data = frame.substring(0, sep2);
  int sum = 0;
  for (unsigned int i = 0; i < data.length(); i++) sum += data[i];
  int checksum = sum % 256;
  return checksum == given.toInt();
}

// ===================== WARSTWA STERUJĄCA =====================

// Ruch o określoną odległość (dodatnia – przód, ujemna – tył)
void moveRobot(int distanceCm) {
  int dir = (distanceCm >= 0 ? 1 : -1) * forwardDir;
  analogWrite(LEFT_MOTOR_PIN, dir > 0 ? currentSpeed : 0);
  analogWrite(rightMotorPin, dir > 0 ? currentSpeed : 0);

  delay(abs(distanceCm) * 50);  // emulacja ruchu
  stopRobot();
  Serial.println("<INFO|MOVE_DONE>");
}

// Obrót o zadaną liczbę stopni (dodatnia – prawo, ujemna – lewo)
void rotateRobot(int deg) {
  int dir = (deg >= 0 ? 1 : -1) * rotationDir;
  if (dir > 0) {
    analogWrite(LEFT_MOTOR_PIN, currentSpeed);
    analogWrite(rightMotorPin, 0);
  } else {
    analogWrite(LEFT_MOTOR_PIN, 0);
    analogWrite(rightMotorPin, currentSpeed);
  }

  delay(abs(deg) * 10);  // emulacja obrotu
  stopRobot();
  Serial.println("<INFO|ROT_DONE>");
}

// Zatrzymanie natychmiastowe
void stopRobot() {
  analogWrite(LEFT_MOTOR_PIN, 0);
  analogWrite(rightMotorPin, 0);
}

// Ustawienie prędkości
void setSpeed(int v) {
  currentSpeed = constrain(v, 0, 255);
  Serial.println("<INFO|SPEED_SET|" + String(currentSpeed) + ">");
}

// Odczyt sonaru
void readSonar() {
  int val = analogRead(sonarPin);
  int distance = map(val, 0, 1023, 2, 400); // emulacja cm
  Serial.println("<DATA|B|" + String(distance) + ">");
}

// Odczyt czujnika IR
void readIR() {
  int val = analogRead(irPin);
  Serial.println("<DATA|I|" + String(val) + ">");
}

// ===================== KONFIGURACJA PINÓW I KIERUNKÓW =====================
// np. <C|L9;R10;S0;I1;F1;T-1|SUM>
// L = LEFT_MOTOR_PIN, R = rightMotorPin, S = sonarPin, I = irPin
// F = forwardDir, T = rotationDir
void configureRobot(String params) {
  int idx = 0;
  while (idx < params.length()) {
    int sep = params.indexOf(';', idx);
    if (sep == -1) sep = params.length();
    String token = params.substring(idx, sep);
    char key = token.charAt(0);
    int val = token.substring(1).toInt();

    switch (key) {
      case 'L': LEFT_MOTOR_PIN = val; pinMode(val, OUTPUT); break;
      case 'R': rightMotorPin = val; pinMode(val, OUTPUT); break;
      case 'S': sonarPin = val; pinMode(val, INPUT); break;
      case 'I': irPin = val; pinMode(val, INPUT); break;
      case 'F': forwardDir = (val >= 0) ? 1 : -1; break;
      case 'T': rotationDir = (val >= 0) ? 1 : -1; break;
    }
    idx = sep + 1;
  }
  Serial.println("<INFO|CONFIG_UPDATED>");
}