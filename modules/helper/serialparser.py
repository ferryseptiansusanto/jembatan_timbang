import re

class SerialParser:
    def __init__(self, mask_template):
        self.mask = mask_template
        self.regex = self._compile_mask(mask_template)

    def _compile_mask(self, mask):
        translation = {
            'C': '[A-Z]',
            'N': r'\d',
            'S': '[a-zA-Z]',
            '+': r'\+',
            '.': r'\.',
            ',': ','
        }

        pattern = ''
        for char in mask:
            if char in translation:
                pattern += translation[char]
            else:
                pattern += re.escape(char)

        return re.compile(f'^{pattern}$')

    def validate(self, line):
        return bool(self.regex.match(line))

    def extract_weight(self, line):
        if not self.validate(line):
            return None

        match = re.search(r'([+-]?\d+\.\d+)', line)
        try:
            return float(match.group(1)) if match else None
        except:
            return None

    def extract_unit(self, line):
        match = re.search(r'[a-zA-Z]+$', line)
        return match.group(0) if match else ''