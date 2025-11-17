/*
 * Projekt 2: Stabilizacja kulki na pochylni
 * Zintegrowany kod (P1 Komunikacja + P2 PID)
 */

#include <Wire.h>
#include <Servo.h>

// ======================== KONFIGURACJA =========================
#define SERVO_PIN 9
#define IR_SENSOR_PIN A0
const unsigned long LOOP_INTERVAL = 120; // Pętla PID co 100 ms (spełnia <= 200 ms)

// ======================= ZMIENNE PID ========================
// pid 2 0.7 0.9
float kp = 0.0;
float ki = 0.0;
float kd = 0.0;

float distance_point = 26.0; // Wartość zadana (cm)
float integral = 0.0;
float previousError = 0.0;

// Ograniczenia dla PID
const float OUTPUT_MIN = -40.0; // Maks. wychylenie serwa (w dół)
const float OUTPUT_MAX = 40.0;  // Maks. wychylenie serwa (w górę)
const float INTEGRAL_MIN = -200.0; // Limit anti-windup
const float INTEGRAL_MAX = 200.0;  // Limit anti-windup

// ====================== ZMIENNE SYSTEMOWE ======================
Servo myservo;
int reset_servo = 75; // Pozycja początkowa serwa
int servo_zero = 70; // Pozycja "zero" (poziomo) serwa
unsigned long lastPidTime = 0;
float distance;

// Stany pracy
bool pid_enabled = false;
bool test_mode = false;
bool run_mode = false;

// Stany dla trybu zaliczeniowego
enum RunState { IDLE, PHASE_1, PHASE_2, DONE };
RunState current_run_state = IDLE;
unsigned long run_start_time;
unsigned long phase2_start_time;
float error_sum = 0.0;
int error_count = 0;

// ======================== SETUP ========================
void setup() {
  Serial.begin(9600);
  myservo.attach(SERVO_PIN);
  myservo.write(reset_servo);
  pinMode(IR_SENSOR_PIN, INPUT);

  lastPidTime = millis();
  Serial.println("<READY>");
}

// ======================== PĘTLA GŁÓWNA ========================
void loop() {
  // 1. Obsługa komunikacji (z P1)
  if (Serial.available()) {
    String frame = Serial.readStringUntil('>');
    if (frame.startsWith("<")) {
      frame.remove(0, 1); // usuń '<'
      handleFrame(frame);
    }
  }

  // 2. Obsługa pętli sterowania (jeśli włączona)
  unsigned long currentMillis = millis();
  if (pid_enabled && (currentMillis - lastPidTime >= LOOP_INTERVAL)) {
    // float dt_seconds = (currentMillis - lastPidTime) / 1000.0;
    distance = get_dist(100);
    lastPidTime = millis();
    
    updatePID();
  }
  
  // 3. Obsługa maszyny stanów trybu zaliczeniowego
  if (run_mode) {
    updateRunMode(currentMillis);
  }
}

// =================== FUNKCJE POMOCNICZE ===================

/**
 * Resetuje stan regulatora PID.
 */
void resetPID() {
  integral = 0.0;
  previousError = 0.0;
  myservo.write(reset_servo); // Wróć do pozycji zero
}

/**
 * Odczytuje i uśrednia pomiar z czujnika IR.
 * Zmieniono na 10 próbek, aby uniknąć blokowania pętli (100 trwało zbyt długo).
 */
float get_dist(int n) {
  long sum = 0;
  for (int i = 0; i < n; i++) {
    sum = sum + analogRead(IR_SENSOR_PIN);
  }
  float adc = (float)sum / n;

  // Ta formuła jest specyficzna dla Twojego czujnika.
  // Upewnij się, że zwraca jednostki [cm]
  float distance_cm = 17569.7 * pow(adc, -1.2062); 
  return (distance_cm);
}

// =================== LOGIKA PID ===================

/**
 * Wykonuje jeden krok regulatora PID.
 */
void updatePID() {
  float proportional = distance - distance_point;

  integral = integral + proportional * 0.1;
  integral = constrain(integral, INTEGRAL_MIN, INTEGRAL_MAX);

  float derivative = (proportional - previousError) / 0.1;

  float output = kp * proportional + ki * integral + kd * derivative;

  // 8. Logika trybu zaliczeniowego (zliczanie błędu w Fazie 2)
  if (current_run_state == PHASE_2) {
    error_sum += abs(proportional);
    error_count++;
  }

  // 9. Telemetria (tylko w trybie TEST)
  if (test_mode) {
    // Format: <DATA|T|czas_ms|dystans|uchyb|wyjscie>
    Serial.print("<DATA|T|");
    Serial.print(millis());
    Serial.print("|");
    Serial.print(distance);
    Serial.print("|");
    Serial.print(proportional);
    Serial.print("|");
     Serial.print(integral);
    Serial.print("|");
    Serial.print(output);
    Serial.println(">");
  }

  previousError = proportional;
  // 10. Sterowanie serwem (z ograniczeniami)
  float servo_signal = servo_zero + output;
  servo_signal = constrain(servo_signal, servo_zero + OUTPUT_MIN, servo_zero + OUTPUT_MAX);
  myservo.write(servo_signal);
}

// =================== TRYB ZALICZENIOWY ===================

/**
 * Rozpoczyna procedurę zaliczeniową.
 */
void startRunMode() {
  resetPID();
  pid_enabled = true;
  run_mode = true;
  test_mode = false;
  
  current_run_state = PHASE_1;
  run_start_time = millis();
  error_sum = 0.0;
  error_count = 0;
  
  Serial.println("<INFO|RUN_START>");
}

/**
 * Maszyna stanów dla trybu zaliczeniowego.
 * Wywoływana w każdej pętli loop().
 */
void updateRunMode(unsigned long currentMillis) {
  if (current_run_state == PHASE_1) {
    // Faza 1: Stabilizacja (10 sekund)
    if (currentMillis - run_start_time > 10000) {
      current_run_state = PHASE_2;
      phase2_start_time = currentMillis;
      Serial.println("<INFO|PHASE_2_START>");
    }
  } 
  else if (current_run_state == PHASE_2) {
    // Faza 2: Pomiar MAE (3 sekundy)
    if (currentMillis - phase2_start_time > 3000) {
      current_run_state = DONE;
      finishRunMode();
    }
  }
}

/**
 * Kończy procedurę, oblicza MAE i wysyła wynik.
 */
void finishRunMode() {
  pid_enabled = false;
  run_mode = false;
  current_run_state = IDLE;
  myservo.write(servo_zero); // Wyzeruj serwo

  float mae = (error_count > 0) ? (error_sum / error_count) : 0.0;

  // Wymagany format wyjścia
  Serial.print("<INFO|MAE|");
  Serial.print(mae, 2); // 2 miejsca po przecinku
  Serial.print(">");
}


// ======================== PARSER (z P1, POPRAWIONY) =========================

void handleFrame(String frame) {
  int sep1 = frame.indexOf('|');      // First separator (after CMD)
  int sep2 = frame.lastIndexOf('|');  // Last separator (before CHK)

  // --- NOWA, POPRAWIONA LOGIKA PARSOWANIA ---
  
  // Musi być co najmniej jeden separator
  if (sep1 == -1) {
    Serial.println("<NACK|BAD_FORMAT>");
    return;
  }

  String cmd;
  String param = ""; // Domyślnie pusty parametr
  String checksum;
  String data_for_chk; // Ciąg do obliczenia sumy kontrolnej

  if (sep1 == sep2) {
    // Brak parametru, format: <CMD|CHECKSUM>
    // frame = "R|82"
    cmd = frame.substring(0, sep1);       // "R"
    checksum = frame.substring(sep1 + 1); // "82"
    data_for_chk = cmd;                   // Suma kontrolna liczona z "R"
  } else {
    // Jest parametr, format: <CMD|PARAM|CHECKSUM>
    // frame = "T|15.0|22"
    cmd = frame.substring(0, sep1);             // "T"
    param = frame.substring(sep1 + 1, sep2);    // "15.0"
    checksum = frame.substring(sep2 + 1);       // "22"
    data_for_chk = cmd + "|" + param;           // Suma liczona z "T|15.0"
  }
  
  // --- KONIEC NOWEJ LOGIKI ---

  // Walidacja sumy kontrolnej
  if (!validateChecksum(data_for_chk, checksum)) {
    Serial.println("<NACK|" + cmd + "|CHK_ERR>");
    return;
  }

  // =================== OBSŁUGA KOMEND (dla P2) ===================
  char c = cmd.charAt(0);
  switch (c) {
    // 'T' | <float> | CHK  -> Ustawienie odległości (TARGET)
    case 'T': 
      distance_point = param.toFloat();
      Serial.println("<ACK|T|TARGET_SET:" + param + ">");
      break;

    // 'P' | <float;float;float> | CHK -> Ustawienie Kp, Ki, Kd
    case 'P':
      { // Wymagany blok dla definicji zmiennych w switch
        int sep_ki = param.indexOf(';');
        int sep_kd = param.lastIndexOf(';');
        if (sep_ki == -1 || sep_kd == -1 || sep_kd <= sep_ki) {
          Serial.println("<NACK|P|BAD_PARAM_FORMAT>");
          break;
        }
        kp = param.substring(0, sep_ki).toFloat();
        ki = param.substring(sep_ki + 1, sep_kd).toFloat();
        kd = param.substring(sep_kd + 1).toFloat();
        resetPID(); // Zresetuj PID po zmianie nastaw
        Serial.println("<ACK|P|PID_SET>");
      }
      break;

    // 'Z' | <int> | CHK -> Ustawienie zera serwa
    case 'Z':
      servo_zero = param.toInt();
      myservo.write(servo_zero);
      Serial.println("<ACK|Z|ZERO_SET:" + param + ">");
      break;

    // 'D' | <0 lub 1> | CHK -> Tryb TEST (telemetria)
    case 'D':
      if (param.toInt() == 1) {
        resetPID();
        pid_enabled = true;
        test_mode = true;
        run_mode = false;
        Serial.println("<ACK|D|TEST_MODE_ON>");
      } else {
        pid_enabled = false;
        test_mode = false;
        run_mode = false;
        myservo.write(servo_zero);
        Serial.println("<ACK|D|TEST_MODE_OFF>");
      }
      break;

    // 'R' | (brak) | CHK -> Tryb ZALICZENIOWY (RUN)
    case 'R':
      startRunMode();
      // Wiadomość <ACK> jest wysyłana w startRunMode() lub tuż po
      Serial.println("<ACK|R|RUN_STARTED>"); // Wyraźne potwierdzenie
      break;

    default:
      Serial.println("<NACK|" + cmd + "|UNKNOWN_CMD>");
      return;
  }
}

// ===================== WALIDACJA SUMY KONTROLNEJ (POPRAWIONA) =====================
/**
 * Waliduje sumę kontrolną
 * @param data - Ciąg danych BEZ separatora sumy i sumy (np. "R" lub "T|15.0")
 * @param given - Otrzymana suma kontrolna jako String (np. "82")
 */
bool validateChecksum(String data, String given) {
  int sum = 0;
  for (unsigned int i = 0; i < data.length(); i++) {
    sum += data[i];
  }
  int checksum = sum % 256;
  return checksum == given.toInt();
}
