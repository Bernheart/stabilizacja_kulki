import serial
import time

# pip install pyserial

# ustaw port COM – sprawdź w Menedżerze urządzeń
PORT = "COM4"
BAUDRATE = 9600

# otwarcie portu
arduino = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(5)  # krótka pauza na reset Arduino

print("Połączono z Arduino!")
response = arduino.readline().decode().strip()
if response:
    print("Arduino:", response)

try:
    while True:
        # wysyłanie danych do Arduino
        cmd = input("Wyślij '1' lub '0' do Arduino (q = quit): ")
        if cmd == 'q':
            break
        arduino.write(cmd.encode())

        # odbiór odpowiedzi
        response = arduino.readline().decode().strip()
        if response:
            print("Arduino:", response)

except KeyboardInterrupt:
    print("Zakończono program.")

finally:
    arduino.close()
