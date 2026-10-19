from PyQt5.QtCore import Qt


def apply_thousand_separator(lineedit):
    def on_text_changed():
        text = lineedit.text()
        if not text:
            return

        parts = text.strip().split()
        if not parts:
            return

        def parse_locale_float(s):
            # Fungsi pintar untuk mendeteksi berbagai format angka
            s = str(s).strip()

            # Skenario 1: Mengandung titik DAN koma (contoh: 2.997,0 atau 2,997.0)
            if "." in s and "," in s:
                if s.rfind(".") > s.rfind(","):
                    return float(s.replace(",", ""))  # 2,997.0 (Format US)
                else:
                    return float(s.replace(".", "").replace(",", "."))  # 2.997,0 (Format ID)

            # Skenario 2: HANYA mengandung koma (contoh: 2997,0)
            elif "," in s:
                return float(s.replace(",", "."))

            # Skenario 3: HANYA mengandung titik (contoh: 2997.0 atau 2.997)
            elif "." in s:
                # Bedakan apakah titik ini untuk desimal (Python) atau ribuan (Ketik manual)
                # Jika di belakang titik ada tepat 3 angka, anggap itu ribuan
                bagian_belakang = s.split(".")[1]
                if len(bagian_belakang) == 3:
                    return float(s.replace(".", ""))  # 2.997 (Ribuan ID)
                else:
                    return float(s)  # 2997.0 (Desimal Python)

            # Skenario 4: Angka bulat murni tanpa titik/koma (contoh: 2997)
            return float(s)

        try:
            num = parse_locale_float(parts[0])
            # Format ulang dengan standar Indonesia (1 angka desimal di belakang koma)
            formatted = "{:,.1f}".format(num).replace(",", "_").replace(".", ",").replace("_", ".")
        except ValueError:
            return

        suffix = " ".join(parts[1:])
        final_text = f"{formatted} {suffix}".strip()

        # Cegah Infinite Loop (Jika teks sudah berformat benar, tidak perlu diset ulang)
        if text == final_text:
            return

        lineedit.blockSignals(True)
        lineedit.setText(final_text)
        lineedit.setCursorPosition(len(final_text))
        lineedit.blockSignals(False)

    lineedit.textChanged.connect(on_text_changed)
    lineedit.setAlignment(Qt.AlignRight)