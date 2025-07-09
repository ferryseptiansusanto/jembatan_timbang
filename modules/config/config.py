import os
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, STOPBITS_ONE, STOPBITS_TWO, EIGHTBITS, SEVENBITS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../../database', 'database.db')

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
DEFAULT_COMPORT = "COM3"

# Mask Template untuk berat serial data
REGEX_BERAT_TEMPLATE = r'^[A-Z]{2},[A-Z]{2},\+\d+(?:\.\d+)?kg$'

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
