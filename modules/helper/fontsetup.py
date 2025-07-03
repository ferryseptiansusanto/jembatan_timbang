from PyQt5.QtCore import Qt

def SetupEdLineFont(edtLine, alignment, fontSize=10, isBold=True ):
    edtLine.setAlignment(alignment)
    font = edtLine.font()
    font.setPointSize(fontSize)
    font.setBold(isBold)
    edtLine.setFont(font)

def apply_thousand_separator(lineedit):
    def on_text_changed():
        text = lineedit.text()
        parts = text.strip().split()
        if not parts:
            return

        raw_number = parts[0].replace('.', '').replace(',', '').replace(' ', '')

        try:
            num = float(raw_number)
            formatted = "{:,.1f}".format(num).replace(",", "_").replace(".", ",").replace("_", ".")
        except ValueError:
            return

        suffix = " ".join(parts[1:])  # ambil satuan
        final_text = f"{formatted} {suffix}".strip()

        lineedit.blockSignals(True)
        lineedit.setText(final_text)
        lineedit.setCursorPosition(len(final_text))
        lineedit.blockSignals(False)

    lineedit.textChanged.connect(on_text_changed)
    lineedit.setAlignment(Qt.AlignRight)
