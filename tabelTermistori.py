import serial
import time
import sys

THERMISTOR_BANKS = 8
THERMISTORS_PER_BANK = 8

port_name = 'COM17'

# Configurare serial
ser = serial.Serial()
ser.port = port_name
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 1

print(f"Aștept conectarea la {port_name}...")

while True:
    try:
        ser.open()
        if ser.is_open:
            print(f"Conectat la {port_name}")
            break
    except serial.SerialException:
        time.sleep(1)

# 🔹 Trimite caracterul 'a' după conectare
ser.write(b'a')
ser.flush()  # asigură trimiterea imediată
print("Am trimis caracterul 'a' către uC")

# Matrice 8x8 pentru valorile termistorilor
thermistor_values = [[0 for _ in range(THERMISTORS_PER_BANK)] for _ in range(THERMISTOR_BANKS)]
buffer = []

# Funcție pentru afișare live tabel 8x8 fără a curăța ecranul
def print_table_live():
    # Mută cursorul în colțul de sus
    print("\033[H", end='')  # ANSI escape code pentru "cursor home"
    print("Tabel valori termistori (16x8):")
    print("Bank/ID | " + " ".join(f"{i:^5}" for i in range(THERMISTORS_PER_BANK)))
    print("-" * (16 + 6 * THERMISTORS_PER_BANK))
    for bank in range(THERMISTOR_BANKS):
        row = " ".join(f"{thermistor_values[bank][col]:5}" for col in range(THERMISTORS_PER_BANK))
        print(f"{bank:^7} | {row}")

# Initializează ecranul pentru output live
print("\033[2J", end='')  # ANSI escape code pentru clear screen
print("Aștept primul 0x0a pentru a începe achiziția...")

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            for byte in data:
                if len(buffer) == 0:
                    if byte == 0x0A:
                        buffer.append(byte)
                    continue
                else:
                    buffer.append(byte)

                if len(buffer) == 7:
                    # Decodează pachetul
                    bank_termistor = buffer[2]
                    bank = bank_termistor // THERMISTORS_PER_BANK
                    termistor = bank_termistor % THERMISTORS_PER_BANK
                    value = (buffer[3] << 8) | buffer[4]

                    # Salvează în matrice
                    thermistor_values[bank][termistor] = value

                    # Afișează tabelul live
                    print_table_live()

                    buffer = []

except KeyboardInterrupt:
    print("\nÎnchidere program.")
finally:
    ser.close()