import re

class RegexSerialParser:
    def __init__(self, pattern=None):
        # Gunakan pattern default jika tidak disediakan
        self.regex = re.compile(pattern or r'^[A-Z]{2},[A-Z]{2},\+\d+(?:\.\d+)?[a-zA-Z]{2}$')

    def clean(self, data):
        if isinstance(data, bytes):
            data = data.decode(errors='ignore')
        return data.strip()

    def validate(self, line):
        return bool(self.regex.match(self.clean(line)))

    def extract_weight(self, line):
        try:
            line = self.clean(line)
            match = re.search(r'([+-]?\d+(?:\.\d+)?)', line)
            return float(match.group(1)) if match else None
        except Exception as e:
            print("[ERROR] extract_weight:", e)
            return None

    def extract_unit(self, line):
        try:
            line = self.clean(line)
            match = re.search(r'[a-zA-Z]+$', line)
            return match.group(0) if match else None
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