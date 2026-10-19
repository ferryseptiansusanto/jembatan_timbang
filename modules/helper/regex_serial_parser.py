import re
from modules.config import config
class RegexSerialParser:
    def __init__(self, pattern=None):
        self.regex = re.compile(pattern)

    def clean(self, data):
        if isinstance(data, bytes):
            data = data.decode(errors='ignore')
        return data.strip()

    def validate(self, line):
        return bool(self.regex.match(self.clean(line)))

    def extract_weight(self, line):
        try:
            line =self.clean(line)
            # 1. Regex mencocokkan dan mengambil angkanya (misal dapat "000510")
            match = re.search(self.regex, line)
            if match:
                raw_weight_str = match.group(1)

                # 2. Logika Python untuk membalik string jika konfigurasi aktif
                if hasattr(config, 'REVERSE_WEIGHT') and config.REVERSE_WEIGHT:
                    raw_weight_str = raw_weight_str[::-1]  # "000510" otomatis jadi "015000"

                return float(raw_weight_str)
            return None
        except Exception as e:
            print("[ERROR] extract_weight:", e)
            return None


    def extract_unit(self, line):
        try:
            line = self.clean(line)
            # Regex kecil khusus untuk mengambil satuan (kg/t/ton) jika ada di belakang string
            match = re.search(r'([a-zA-Z]{1,3})\s*$', line)
            return match.group(1).lower() if match else "kg"
        except Exception as e:
            print("[ERROR] extract_unit:", e)
            return None

    def format_weight_locale(self, weight, unit='kg'):
        try:
            rounded = round(weight, 1)
            integer, decimal = str(rounded).split(".")
            formatted = f"{int(integer):,}".replace(",", ".")
            return f"{formatted},{decimal} {unit}".strip()
        except:
            return f"0,0 {unit}"