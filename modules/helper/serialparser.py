import re

class SerialParser:
    def __init__(self, mask_template):
        self.mask = mask_template
        self.regex = self._compile_mask(mask_template)

    def _compile_mask(self, mask):
        translation = {
            'C': '[A-Z]',      # Uppercase
            'N': r'\d',        # Digit
            'S': '[a-zA-Z]',   # Any letter
            '+': r'\+',        # Literal plus
            '.': r'\.',        # Literal dot
            ',': re.escape(',') # Literal comma
        }

        pattern = ''
        for char in mask:
            pattern += translation.get(char, re.escape(char))

        return re.compile(f'^{pattern}$')

    def validate(self, line):
        line = line.strip()

        return bool(self.regex.match(line))

    def extract_weight(self, line):

        if not self.validate(line):
            return None
        print("[DEBUG] Raw weight value:", line)
        # Regex yang fleksibel: angka bulat, desimal, koma di akhir
        match = re.search(r'([+-]?\d+(?:\.\d*)?)', line)
        if not match:
            return None

        raw = match.group(1)
        try:
            print("[DEBUG] Weight string extracted:", raw)

            return float(raw)
        except ValueError:
            cleaned = raw.rstrip('.')  # misal +123456.
            try:
                return float(cleaned)
            except:
                return None

    def extract_unit(self, line):
        if not self.validate(line):
            return None
        match = re.search(r'[a-zA-Z]+$', line)
        return match.group(0) if match else None

    def format_weight_locale(self, weight):
        try:
            rounded = round(float(weight), 1)
            integer_part, decimal_part = str(rounded).split(".")
            formatted_int = f"{int(integer_part):,}".replace(",", ".")
            return f"{formatted_int},{decimal_part}"
        except:
            return "0,0"