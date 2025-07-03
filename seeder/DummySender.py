import serial
import time
import random

# === KONFIGURASI ===
DUMMY_PORT = "COM1"        # Ganti sesuai port tujuan
BAUDRATE = 9600            # Contoh: 2400, 4800, 9600
DATA_BITS = 8              # 7 atau 8
PARITY = "N"               # N (None), E (Even), O (Odd)
STOP_BITS = 1              # 1 atau 2

INTERVAL = 1               # Detik antar kiriman
DUMMY_STRING = "US,GS,+00123.4kg\r\n"

# === KONVERSI PARAMETER SERIAL ===
bytesize_map = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}
parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
stopbits_map = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}

try:
    ser = serial.Serial(
        port=DUMMY_PORT,
        baudrate=BAUDRATE,
        bytesize=bytesize_map[DATA_BITS],
        parity=parity_map[PARITY.upper()],
        stopbits=stopbits_map[STOP_BITS],
        timeout=1
    )
    print(f"[DUMMY ACTIVE] Kirim ke {DUMMY_PORT} @ {BAUDRATE}bps, {DATA_BITS}{PARITY}{STOP_BITS}")
    while True:
        weight = round(random.uniform(0, 9999.9), 1)  # Berat acak: 0.0 - 9999.9
        formatted_weight = f"US,GS,+{weight:07.1f}kg\r\n"  # Format menjadi "+00123.4kg"
        ser.write(formatted_weight.encode())
        print(f"[SEND] {formatted_weight.strip()}")
        time.sleep(INTERVAL)


except KeyboardInterrupt:
    print("\n[EXIT] Program dihentikan manual lewat Ctrl+C")
    ser.close()

except Exception as e:
    print(f"[ERROR] {e}")
