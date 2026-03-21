import serial
import threading

PORT = "COM17"
BAUDRATE = 9600

def read_from_port(ser):
    while ser.is_open:
        try:
            data = ser.readline().decode("utf-8", errors="ignore").strip()
            if data:
                print(f"\n[RX] {data}")
        except Exception as e:
            print(f"Read error: {e}")
            break

def main():
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

        print(f"Conectat la {PORT} @ {BAUDRATE} baud")

        # Thread pentru citire
        rx_thread = threading.Thread(target=read_from_port, args=(ser,), daemon=True)
        rx_thread.start()

        # Scriere din tastatură
        while True:
            msg = input("[TX] ")
            ser.write((msg + "\r\n").encode("utf-8"))

    except serial.SerialException as e:
        print(f"Eroare serială: {e}")
    except KeyboardInterrupt:
        print("\nÎnchidere aplicație...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port închis.")

if __name__ == "__main__":
    main()