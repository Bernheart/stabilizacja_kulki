# --- VIRTUAL ENVIROMENT ---
python -m venv venv
source venv/bin/activate   # macOS / Linux
# or venv\Scripts\activate on Windows


# --- DEPENDENCIES ---
pip install -r requirements.txt


# --- CODE ---
# change lib/config/config.yaml if neccesery
python -m lib.main


# --- TEST ---
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# change ports in config and fake_arduino
python lib/test/fake_arduino.py

# best
pid 2 0.7 0.9
[RESULT] <INFO|MAE|0.14> (in cm)
