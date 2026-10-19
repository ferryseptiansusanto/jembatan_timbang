import os
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, STOPBITS_ONE, STOPBITS_TWO, EIGHTBITS, SEVENBITS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../../database', 'database.db')
#DB_PATH = os.path.normpath(os.path.join(BASE_DIR, '../../database', 'database.db'))

TABLES = {
    "TblBarang": "db_master_barang",
    "TblPelanggan": "db_master_pelanggan",
    "TblPemasok": "db_master_pemasok",
    "TblUser": "db_master_user",
    "TblProperties": "db_properties",
    "TblTransaksiPelanggan": "db_transaksi_pelanggan",
    "TblTransaksiPemasok": "db_transaksi_pemasok",
}

# COM setting options
BAUDRATES = ["110", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200"]
DATABITS = ["5", "6", "7", "8"]
STOPBITS = ["1", "1.5", "2"]
PARITY = ["None", "Even", "Odd", "Mark", "Space"]
FLOWCONTROL = ["None", "RTS/CTS", "XON/XOFF"]

PARITY_MAP = {
    "N": PARITY_NONE,
    "E": PARITY_EVEN,
    "O": PARITY_ODD
}
STOPBITS_MAP = {
    1: STOPBITS_ONE,
    2: STOPBITS_TWO
}
BYTESIZE_MAP = {
    7: SEVENBITS,
    8: EIGHTBITS
}


# (Opsional) Default COM port jika perlu
DEFAULT_COMPORT = "COM1"

# Mask Template untuk berat serial data
# =====================================================================
# 1. TEMPLATE GSC / CAS (Sangat Lengkap & Simulator Angka Murni)
# Contoh Match 1: "ST,NT,+15000kg\r\n"  (Format asli GSC)
# Contoh Match 2: "US,GS,+500.5\r"      (Unstable, Gross)
# Contoh Match 3: "015000"              (Angka murni dari simulator)
# =====================================================================
REGEX_BERAT_TEMPLATE = r'^(?:[A-Z]{2},[A-Z]{2},\+)?(\d+(?:\.\d+)?)(?:kg)?\s*$'


# =====================================================================
# 2. TEMPLATE TOLEDO / IND (Karakter Tersembunyi STX)
# Catatan: \x02 adalah Start of Text, A/B adalah status motion.
# Contoh Match 1: "\x02A  015000\r\n"   (Status A = Valid/Stabil)
# Contoh Match 2: "\x02B 15000.5\r"     (Status B = Goyang/Motion)
# Contoh Match 3: "\x02 15000"
# =====================================================================
#REGEX_BERAT_TEMPLATE = r'^\x02[A-Z]?\s*(\d+(?:\.\d+)?)\s*\r?\n?$'


# =====================================================================
# 3. TEMPLATE AVERY (Karakter Tersembunyi STX & ETX)
# Catatan: \x03 adalah End of Text. G/N adalah Gross/Netto.
# Contoh Match 1: "\x02 +  15000 kg G \x03"
# Contoh Match 2: "\x02 - 00500 kg N \x03"
# Contoh Match 3: "\x02+15000G\x03"
# =====================================================================
#REGEX_BERAT_TEMPLATE = r'^\x02\s*[+-]\s*(\d+(?:\.\d+)?)\s*(?:kg)?\s*[A-Z]\s*\x03$'


# =====================================================================
# 4. TEMPLATE A&D / EXCELL / SONIC (Pola 2 Huruf Awal)
# Contoh Match 1: "ST,+015000  kg\r\n"
# Contoh Match 2: "US,-00500 kg\r"
# Contoh Match 3: "ST,15000"
# =====================================================================
#REGEX_BERAT_TEMPLATE = r'^[A-Z]{2},[+-]?(\d+(?:\.\d+)?)\s*(?:kg)?\s*$'


# =====================================================================
# 5. TEMPLATE YAOHUA / GENERIC CHINA (Pola Mentah Sederhana)
# Catatan: Sering dipakai juga untuk format angka Reversed (Terbalik).
# Contoh Match 1: "=015000\r\n"
# Contoh Match 2: "+015000\r"
# Contoh Match 3: "15000"
# =====================================================================
#REGEX_BERAT_TEMPLATE = r'^[=+-]?(\d+(?:\.\d+)?)\s*$'

#Jika data pembacaannya terbalik True, jika tidak false
# Contoh data 000510 value terbaca 15000 jika true
REVERSE_WEIGHT = False

def map_parity(code):
    return PARITY_MAP.get(code.upper(), PARITY_NONE)

def map_stopbits(value):
    return STOPBITS_MAP.get(int(value), STOPBITS_ONE)

def map_bytesize(value):
    return BYTESIZE_MAP.get(int(value), EIGHTBITS)

def get_config_path(filename="perusahaan.xml"):
    appdata = os.getenv("APPDATA")  # Contoh: C:\Users\ferry\AppData\Roaming
    config_dir = os.path.join(appdata, "JembatanTimbang")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, filename)
