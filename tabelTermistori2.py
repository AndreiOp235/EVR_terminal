import serial
import time

THERMISTOR_BANKS = 8
THERMISTORS_PER_BANK = 8
port_name = 'COM17'
PACKET_SIZE = 7
PACKET_HEADER = 0x0A
PACKET_FOOTER = 0xFF
RESYNC_TIMEOUT = 3.0
KEEPALIVE_INTERVAL = 5.0

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

def send_trigger():
    ser.write(b'a')
    ser.flush()
    print(">>> Trimis 'a' către uC")

send_trigger()

thermistor_values = [[0] * THERMISTORS_PER_BANK for _ in range(THERMISTOR_BANKS)]
buffer = []
last_valid_packet_time = time.time()
last_keepalive_time = time.time()
packets_received = 0
sync_errors = 0
crc_errors = 0

def print_table_live():
    print("\033[H", end='')
    print(f"Termistori live | Pachete OK: {packets_received} | Sync err: {sync_errors} | CRC err: {crc_errors}     ")
    print("Bank/ID | " + " ".join(f"{i:^5}" for i in range(THERMISTORS_PER_BANK)))
    print("-" * (10 + 6 * THERMISTORS_PER_BANK))
    for bank in range(THERMISTOR_BANKS):
        row = " ".join(f"{thermistor_values[bank][col]:5}" for col in range(THERMISTORS_PER_BANK))
        print(f"  {bank:^5} | {row}")

def is_valid_packet(buf):
    """
    Validează structura pachetului:
      [0] = 0x0A  header
      [1] = 0x00  fix zero
      [2] = index termistor (0..63)
      [3] = MSB valoare
      [4] = LSB valoare
      [5] = CRC   (verificat separat pentru a număra erorile distinct)
      [6] = 0xFF  footer
    """
    if len(buf) != PACKET_SIZE:
        return False, "lungime"
    if buf[0] != PACKET_HEADER:
        return False, "header"
    if buf[6] != PACKET_FOOTER:
        return False, "footer"
    if buf[1] != 0x00:
        return False, "byte1"
    index = buf[2]
    if index >= THERMISTOR_BANKS * THERMISTORS_PER_BANK:
        return False, "index"
    return True, "ok"

def crc_matches(buf):
    """
    Înlocuiește cu logica exactă din CRC_calculate() de pe uC.
    Momentan returnează True (skip CRC) — trimite-mi funcția C să o port.
    """
    return True

print("\033[2J", end='')
print("Aștept primul 0x0A pentru a începe achiziția...")

try:
    while True:
        now = time.time()

        # Keepalive preventiv
        if now - last_keepalive_time > KEEPALIVE_INTERVAL:
            send_trigger()
            last_keepalive_time = now

        # Timeout resincronizare
        if now - last_valid_packet_time > RESYNC_TIMEOUT:
            print(f"\n[WARN] Niciun pachet valid de {RESYNC_TIMEOUT}s — resetez și retrimis 'a'")
            buffer.clear()
            ser.reset_input_buffer()
            send_trigger()
            last_valid_packet_time = now
            last_keepalive_time = now
            time.sleep(0.1)
            continue

        if ser.in_waiting == 0:
            time.sleep(0.005)
            continue

        data = ser.read(ser.in_waiting)

        for byte in data:
            # Căutăm header-ul dacă buffer-ul e gol
            if len(buffer) == 0:
                if byte == PACKET_HEADER:
                    buffer.append(byte)
                continue

            buffer.append(byte)

            # Verificare rapidă: dacă al 7-lea byte nu e footer, resincronizare imediată
            if len(buffer) == PACKET_SIZE:
                valid, reason = is_valid_packet(buffer)

                if valid:
                    if not crc_matches(buffer):
                        crc_errors += 1
                        # Pachet structural OK dar CRC greșit — poate fi zgomot pe linie
                        # Îl ignorăm dar nu resetăm sync-ul
                        buffer = []
                        continue

                    # Pachet complet și valid ✅
                    index = buffer[2]
                    bank = index // THERMISTORS_PER_BANK
                    termistor = index % THERMISTORS_PER_BANK
                    value = (buffer[3] << 8) | buffer[4]

                    thermistor_values[bank][termistor] = value
                    packets_received += 1
                    last_valid_packet_time = time.time()
                    last_keepalive_time = time.time()
                    print_table_live()
                    buffer = []

                else:
                    sync_errors += 1
                    # Slide window: caută următorul 0x0A în buffer curent
                    new_start = -1
                    for i in range(1, len(buffer)):
                        if buffer[i] == PACKET_HEADER:
                            new_start = i
                            break
                    buffer = buffer[new_start:] if new_start != -1 else []

except KeyboardInterrupt:
    print("\nÎnchidere program.")
finally:
    ser.close()