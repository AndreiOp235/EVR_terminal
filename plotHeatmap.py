import serial
import time
import tkinter as tk
import threading

THERMISTOR_BANKS = 16
THERMISTORS_PER_BANK = 8
port_name = 'COM17'

PACKET_SIZE = 7
PACKET_HEADER = 0x0A
PACKET_FOOTER = 0xFF

RESYNC_TIMEOUT = 3.0
KEEPALIVE_INTERVAL = 5.0
SERIAL_RESET_INTERVAL = 3.0   # reset serial la fiecare 10 sec

VALUE_MIN = 0
VALUE_MAX = 4000
UI_REFRESH_MS = 100

EXCLUDE = [(3,3), (6,5), (8,1), (9,0), (13,3)]  # bank x thermistor de eliminat din medie

def calculate_mean(values):
    total = 0
    count = 0
    for i, row in enumerate(values):
        for j, val in enumerate(row):
            if (i,j) in EXCLUDE:
                continue
            total += val
            count += 1
    return total / count if count > 0 else 0

def jet_color(value, vmin=VALUE_MIN, vmax=VALUE_MAX):
    t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    r = min(1.0, max(0.0, 1.5 - abs(4*t - 3)))
    g = min(1.0, max(0.0, 1.5 - abs(4*t - 2)))
    b = min(1.0, max(0.0, 1.5 - abs(4*t - 1)))
    return r, g, b


def rgb_to_hex(r, g, b):
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'


def text_color_for_bg(r, g, b):
    return 'black' if (0.299*r + 0.587*g + 0.114*b) > 0.55 else 'white'


class HeatmapApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Termistori Heatmap")
        self.root.configure(bg='#1e1e1e')

        self._lock = threading.Lock()

        self._values = [[0]*THERMISTORS_PER_BANK for _ in range(THERMISTOR_BANKS)]
        self._dirty = True

        self._packets = 0
        self._sync_err = 0
        self._crc_err = 0

        self._status = "Conectare..."

        CELL_W = 80
        CELL_H = 60
        LABEL_W = 50
        HEADER_H = 36
        COLORBAR_W = 60
        PAD = 10

        grid_w = THERMISTORS_PER_BANK * CELL_W
        grid_h = THERMISTOR_BANKS * CELL_H

        total_w = LABEL_W + grid_w + COLORBAR_W + PAD*3
        total_h = HEADER_H + grid_h + 36 + PAD*2

        self.root.geometry(f"{total_w}x{total_h}")

        self.title_var = tk.StringVar(value="Aștept date...")

        tk.Label(root,
                 textvariable=self.title_var,
                 bg='#1e1e1e',
                 fg='#cccccc',
                 font=('Consolas',10)).place(x=PAD,y=PAD)

        for j in range(THERMISTORS_PER_BANK):

            tk.Label(root,
                     text=f"P{j}",
                     bg='#1e1e1e',
                     fg='#999999',
                     font=('Consolas',9),
                     width=6).place(
                x=LABEL_W + PAD + j*CELL_W + CELL_W//2 - 20,
                y=HEADER_H - 2)

        for i in range(THERMISTOR_BANKS):

            tk.Label(root,
                     text=f"B{i}",
                     bg='#1e1e1e',
                     fg='#999999',
                     font=('Consolas',9)).place(
                x=PAD,
                y=HEADER_H + PAD + i*CELL_H + CELL_H//2 - 8)

        canvas_x = LABEL_W + PAD
        canvas_y = HEADER_H + PAD

        self.canvas = tk.Canvas(root,
                                width=grid_w,
                                height=grid_h,
                                highlightthickness=0,
                                bg='#111111')

        self.canvas.place(x=canvas_x,y=canvas_y)

        self.rects = []
        self.texts = []

        for i in range(THERMISTOR_BANKS):

            row_r = []
            row_t = []

            for j in range(THERMISTORS_PER_BANK):

                x0 = j*CELL_W
                y0 = i*CELL_H

                rect = self.canvas.create_rectangle(
                    x0,y0,x0+CELL_W,y0+CELL_H,
                    fill='#1a1a2e',
                    outline='#333333',
                    width=1)

                text = self.canvas.create_text(
                    x0+CELL_W//2,
                    y0+CELL_H//2,
                    text='0',
                    fill='white',
                    font=('Consolas',11,'bold'))

                row_r.append(rect)
                row_t.append(text)

            self.rects.append(row_r)
            self.texts.append(row_t)

        self.status_var = tk.StringVar(value="")

        tk.Label(root,
                 textvariable=self.status_var,
                 bg='#1e1e1e',
                 fg='#666666',
                 font=('Consolas',8)).place(
            x=PAD,
            y=HEADER_H + PAD + grid_h + 4)

        self.root.after(UI_REFRESH_MS,self._ui_refresh)


    def push_value(self,bank,thermistor,value,packets,sync_err,crc_err):

        with self._lock:

            self._values[bank][thermistor] = value
            self._packets = packets
            self._sync_err = sync_err
            self._crc_err = crc_err
            self._dirty = True


    def set_status(self,msg):

        with self._lock:

            self._status = msg
            self._dirty = True


    def _ui_refresh(self):

        with self._lock:

            if not self._dirty:

                self.root.after(UI_REFRESH_MS,self._ui_refresh)
                return

            values = [row[:] for row in self._values]

            packets = self._packets
            sync_err = self._sync_err
            crc_err = self._crc_err
            status = self._status

            self._dirty = False

        for i in range(THERMISTOR_BANKS):

            for j in range(THERMISTORS_PER_BANK):

                v = values[i][j]

                r,g,b = jet_color(v)

                self.canvas.itemconfig(
                    self.rects[i][j],
                    fill=rgb_to_hex(r,g,b))

                self.canvas.itemconfig(
                    self.texts[i][j],
                    text=str(v),
                    fill=text_color_for_bg(r,g,b))
        mean_value = calculate_mean(values)
        self.title_var.set(
            f"Termistori live | Pachete OK: {packets} | Sync err: {sync_err} | Media termistorilor: {mean_value:.1f}")

        self.status_var.set(status)

        self.root.after(UI_REFRESH_MS,self._ui_refresh)


def serial_thread(app):

    ser = serial.Serial()

    ser.port = port_name
    ser.baudrate = 115200
    ser.timeout = 1

    app.set_status(f"Conectare la {port_name}...")

    while True:

        try:

            ser.open()

            if ser.is_open:

                app.set_status(f"Conectat la {port_name}")
                break

        except serial.SerialException:

            time.sleep(1)

    def send_trigger():

        ser.write(b'a')
        ser.flush()

    send_trigger()

    buffer = []

    packets_received = 0
    sync_errors = 0
    crc_errors = 0

    last_valid = time.time()
    last_keepalive = time.time()
    last_serial_reset = time.time()

    def is_valid(buf):

        if len(buf) != PACKET_SIZE:
            return False

        if buf[0] != PACKET_HEADER or buf[6] != PACKET_FOOTER:
            return False

        return True

    try:

        while True:

            now = time.time()

            if now - last_serial_reset > SERIAL_RESET_INTERVAL:

                app.set_status("Restart serial (timer)")

                ser.close()

                time.sleep(0.5)

                ser.open()

                ser.reset_input_buffer()

                send_trigger()

                last_serial_reset = time.time()

            if ser.in_waiting == 0:

                time.sleep(0.002)
                continue

            data = ser.read(ser.in_waiting)

            for byte in data:

                if len(buffer) == 0:

                    if byte == PACKET_HEADER:
                        buffer.append(byte)

                    continue

                buffer.append(byte)

                if len(buffer) == PACKET_SIZE:

                    if is_valid(buffer):

                        idx = buffer[2]

                        bank = idx // THERMISTORS_PER_BANK
                        term = idx % THERMISTORS_PER_BANK

                        value = (buffer[3] << 8) | buffer[4]

                        packets_received += 1

                        app.push_value(
                            bank,
                            term,
                            value,
                            packets_received,
                            sync_errors,
                            crc_errors)

                    else:

                        sync_errors += 1

                    buffer = []

    finally:

        ser.close()


if __name__ == '__main__':

    root = tk.Tk()

    app = HeatmapApp(root)

    t = threading.Thread(target=serial_thread,args=(app,),daemon=True)
    t.start()

    root.mainloop()