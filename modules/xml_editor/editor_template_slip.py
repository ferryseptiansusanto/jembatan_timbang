from PyQt5 import QtWidgets
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtGui import QTextDocument
from modules.helper.xmlconfigurator import bacaslipxml, tulis_slipxml, baca_konfigurasi


class TemplateSlipEditor(QtWidgets.QWidget):
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.setWindowTitle("Editor Template Slip")
        self.resize(600, 700)

        self.editor = QtWidgets.QTextEdit()
        self.btnLoad = QtWidgets.QPushButton("Buka dari XML")
        self.btnSave = QtWidgets.QPushButton("Simpan ke XML")
        self.btnPreview = QtWidgets.QPushButton("Preview Cetak")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.btnLoad)
        layout.addWidget(self.btnSave)
        layout.addWidget(self.btnPreview)
        self.setLayout(layout)

        self.btnLoad.clicked.connect(self.load_template)
        self.btnSave.clicked.connect(self.save_template)
        self.btnPreview.clicked.connect(self.preview_template)

    def load_template(self):
        html = bacaslipxml()
        self.editor.setPlainText(html)

    def save_template(self):
        html = self.editor.toPlainText().strip()
        tulis_slipxml(html)
        QtWidgets.QMessageBox.information(self, "Simpan", "Template berhasil disimpan ke konfigurasi.")

    def preview_template(self):
        html = self.editor.toPlainText()
        preview = QPrintPreviewDialog()

        def render(printer):
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print(printer)  # ✅ Inilah bagian yang hilang

        preview.paintRequested.connect(render)
        preview.exec_()