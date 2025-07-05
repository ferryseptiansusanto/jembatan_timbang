import serial
import time
import random

# === KONFIGURASI ===
PORT = "COM1"              # Ganti sesuai kebutuhan
BAUDRATE = 9600
DATA_BITS = 8
PARITY = "N"
STOP_BITS = 1
INTERVAL = 0.2             # Kirim setiap 0.5 detik

# === SERIAL SETUP ===
bytesize_map = {7: serial.SEVENBITS, 8: serial.EIGHTBITS}
parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
stopbits_map = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}
INDICATOR_TYPE = "A12"  # Pilihan: "D10", "T1", "AND", "A12", "D2002E", "SMART"

# === GENERATOR FRAME D10 ===
def make_d10_frame(weight: float, desimal_pos: int = None) -> bytes:
    """
    weight       : nilai berat asli (boleh float)
    desimal_pos  : posisi titik desimal (0–4), jika None → acak
    """
    value = f"{abs(int(weight * 10 ** 4)):07d}"[:7]  # 7 digit angka
    posisi = str(desimal_pos) if desimal_pos is not None else random.choice("43210")
    return b'\x02' + value.encode() + posisi.encode() + b'\x03'


def make_t1_frame(value: int) -> bytes:
    """
    value : int dengan maksimal 7 digit
    Reverse string, kirim setelah simbol '='
    """
    str_val = f"{value:07d}"[:7]       # Pastikan 7 digit
    reversed_str = str_val[::-1]       # Balik urutan karakter
    return b'=' + reversed_str.encode()  # Awali dengan '='

# === FRAME GENERATOR UNTUK AND ===
def make_and_frame(value: int) -> bytes:
    """
    value: int maksimal 8 digit
    Format kirim: G + 10 karakter (termasuk header), berat dari index ke-2 s/d ke-9
    """
    str_val = f"{value:08d}"  # Format berat jadi 8 digit
    frame = "G" + "00" + str_val  # Tambahkan 2 karakter dummy di index 0–1
    return frame.encode()

# === FRAME GENERATOR UNTUK A12 ===
def make_a12_simple_frame(value: int) -> bytes:
    """
    Simulasi data untuk method Timbangan_A12E VB
    Format: 'n' + 6 digit angka
    """
    str_val = f"{value:06d}"[:6]  # 6 digit fixed
    return b'n' + str_val.encode()

# === FRAME GENERATOR UNTUK D2002E ===
def make_d2002e_frame(value: int) -> bytes:
    """
    value: int maksimal 7 digit
    Format: = + reversed string
    """
    str_val = f"{value:07d}"[:7]       # Format ke 7 digit
    reversed_str = str_val[::-1]       # Balik urutan karakter
    return b'=' + reversed_str.encode()

# === FRAME GENERATOR UNTUK SMART ===
def make_smart_frame(weight: int) -> bytes:
    """
    weight: integer 8 digit max
    Format: STX + 8 digit angka berat
    """
    str_val = f"{weight:08d}"[:8]       # Format ke 8 digit
    return b'\x02' + str_val.encode()

# === MAIN LOOP ===
try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=bytesize_map[DATA_BITS],
        parity=parity_map[PARITY],
        stopbits=stopbits_map[STOP_BITS],
        timeout=1
    )
    print(f"[DUMMY ACTIVE] Mode: {INDICATOR_TYPE} @ {BAUDRATE}bps")

    while True:
        if INDICATOR_TYPE == "D10":
            berat = round(random.uniform(0.0, 9999.99), 4)
            frame = make_d10_frame(berat)
        elif INDICATOR_TYPE == "T1":
            berat_int = random.randint(0, 9999999)
            frame = make_t1_frame(berat_int)
        elif INDICATOR_TYPE == "AND":
            berat_int = random.randint(0, 99999999)
            frame = make_and_frame(berat_int)
        elif INDICATOR_TYPE == "A12":
            berat = random.randint(0, 999999)
            frame = make_a12_simple_frame(berat)
        elif INDICATOR_TYPE == "D2002E":
            berat_int = random.randint(0, 9999999)
            frame = make_d2002e_frame(berat_int)
        elif INDICATOR_TYPE == "SMART":
            berat_int = random.randint(0, 99999999)
            frame = make_smart_frame(berat_int)
        else:
            frame = b"[UNKNOWN TIMBANGAN]\n"

        ser.write(frame)
        print(f"[SEND] {frame}")
        time.sleep(INTERVAL)


except KeyboardInterrupt:
    print("\n[EXIT] Seeder dihentikan.")
    ser.close()

except Exception as e:
    print(f"[ERROR] {e}")