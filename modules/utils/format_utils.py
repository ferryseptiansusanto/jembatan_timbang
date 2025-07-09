from PyQt5.QtCore import Qt


def apply_thousand_separator(lineedit):
    def on_text_changed():
        text = lineedit.text()
        parts = text.strip().split()
        if not parts:
            return

        def parse_locale_float(s):
            return float(s.replace(".", "").replace(",", "."))

        try:
            num = parse_locale_float(parts[0])
            formatted = "{:,.1f}".format(num).replace(",", "_").replace(".", ",").replace("_", ".")
        except ValueError:
            return

        suffix = " ".join(parts[1:])
        final_text = f"{formatted} {suffix}".strip()

        lineedit.blockSignals(True)
        lineedit.setText(final_text)
        lineedit.setCursorPosition(len(final_text))
        lineedit.blockSignals(False)

    lineedit.textChanged.connect(on_text_changed)
    lineedit.setAlignment(Qt.AlignRight)
