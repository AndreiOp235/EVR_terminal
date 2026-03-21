import serial
import struct
import os
import sys

# Open the serial port COM11 with a baud rate of 9600 (adjust as needed)
ser = serial.Serial('COM9', 115200, timeout=1)

print("Listening on COM11...")

def ceva1():
    try:
        while True:
            packets = []  # Store two valid packets

            while len(packets) < 2:  # Read two full packets
                if ser.in_waiting >= 4:  # Ensure at least 4 bytes are available
                    buffer = ser.read(4)  # Read 4 bytes

                    # Ensure the packet starts with 12
                    if buffer[0] != 12:
                        print(f"Warning: First byte is {buffer[0]}, expected 12. Dropping packet.")
                        continue  # Skip this set of bytes

                    # Extract the 16-bit integer from bytes [1:3]
                    value = struct.unpack('<H', buffer[1:3])[0]
                    packets.append(value)

            # Print the values from two packets
            print(f"Current: {packets[0]} ->> {packets[1]}")

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()  # Close the serial port when done


def ceva2():
    try:
        while True:
            if ser.in_waiting >= 4:  # Ensure at least 4 bytes are available
                buffer = ser.read(4)  # Read 4 bytes

                # Drop the first byte (must be 12)
                if buffer[0] != 12:
                    print(f"Warning: First byte is {buffer[0]}, expected 12. Dropping packet.")
                    continue  # Skip this set of bytes

                # Combine the next two bytes into a 16-bit integer (Little Endian)
                value = struct.unpack('>H', buffer[1:3])[0]  # '<H' means little-endian 16-bit unsigned

                # Print the value
                print(f"Current: {value}")

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()  # Close the serial port when done


ceva2()