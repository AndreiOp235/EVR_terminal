import serial
import time
import os
import csv

THERMISTOR_BANKS = 8
THERMISTORS_PER_BANK = 8
MAX_FRAMES = 20

port_name = 'COM17'

ser = serial.Serial()
ser.port = port_name
ser.baudrate = 9600
ser.timeout = 1

print(f"Aștept conectarea la {port_name}...")

while True:
    try:
        ser.open()
        if ser.is_open:
            print("Conectat!")
            break
    except serial.SerialException:
        time.sleep(1)

# Trimite 'a'
time.sleep(0.2)
ser.write(b'a')
ser.flush()
print("Trimis 'a'")

# Matrice curentă 8x8
thermistor_values = [[0]*THERMISTORS_PER_BANK for _ in range(THERMISTOR_BANKS)]
buffer = []

all_frames = []
frame_counter = 0
received_ids = set()

print("Încep achiziția...")

try:
    while frame_counter < MAX_FRAMES:

        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)

            for byte in data:

                # caută început pachet
                if len(buffer) == 0:
                    if byte == 0x0A:
                        buffer.append(byte)
                    continue
                else:
                    buffer.append(byte)

                # pachet complet
                if len(buffer) == 7:

                    term_id = buffer[2]
                    bank = term_id // THERMISTORS_PER_BANK
                    col = term_id % THERMISTORS_PER_BANK
                    value = (buffer[3] << 8) | buffer[4]

                    thermistor_values[bank][col] = value
                    received_ids.add(term_id)

                    buffer = []

                    # dacă am primit toate cele 64 valori
                    if len(received_ids) == 64:
                        frame_counter += 1
                        print(f"Frame {frame_counter} salvat")
                        
                        # salvare copie matrice
                        all_frames.append([row[:] for row in thermistor_values])

                        received_ids.clear()

    print("Achiziție completă!")

finally:
    ser.close()

# ==============================
# Salvare CSV-uri
# ==============================

os.makedirs("CSV", exist_ok=True)

for idx, frame in enumerate(all_frames, start=1):
    filename = f"CSV/frame_{idx:03d}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(frame)

print("Fișierele CSV au fost generate în folderul 'CSV'")