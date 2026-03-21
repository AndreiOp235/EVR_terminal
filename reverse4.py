import serial


ser = serial.Serial("COM17", 9600)

buffer = []

while True:
    b = ser.read(1)
    if not b:
        continue
    buffer.append(b[0])

    while len(buffer) >= 6:
        frame = buffer[:6]
        if crc_calc == frame[5]:
            # cadru valid!
            index = frame[2]
            value = (frame[3] << 8) | frame[4]
            print(f"Index: {index}  Value: {value}")
            buffer = buffer[6:]  # scoatem cadrul procesat
        else:
            # shift la următorul byte (resync)
            buffer = buffer[1:]