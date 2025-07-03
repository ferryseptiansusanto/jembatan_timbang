
from modules.config.config import BAUDRATES, DATABITS, STOPBITS, PARITY, FLOWCONTROL
from PyQt5 import QtWidgets
from .form_properties import Ui_Form  # pastikan form_user.py ada di folder yang sama
from modules.helper.xmlconfigurator import tulis_konfigurasi, baca_konfigurasi
from modules.helper.serialutils import list_serial_ports

class PropertiesMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.setupUi(self)
        self.connect_signals()
        self.cbbBaudrate.addItems(BAUDRATES)
        self.cbbDatabits.addItems(DATABITS)
        self.cbbStopbits.addItems(STOPBITS)
        self.cbbParity.addItems(PARITY)
        self.cbbFlowcontrol.addItems(FLOWCONTROL)
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.setWindowTitle(f"Setting - Login oleh: {self.current_user}")
        self.refresh_port()
        self.load_record()

    def connect_signals(self):
        self.btnSave.clicked.connect(self.save_record)
        self.btnRefresh.clicked.connect(self.refresh_port)

    def refresh_port(self):
        self.cbbComport.clear()
        self.cbbComport.addItems(list_serial_ports())

    def save_record(self):
        if not self.edNama.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validasi", "Nama perusahaan tidak boleh kosong.")
            return
        data = {
            "nama_perusahaan": self.edNama.text(),
            "alamat": self.txtedAlamat.toPlainText(),
            "telepon": self.edTelepon.text(),
            "comport": self.cbbComport.currentText(),
            "baudrate": self.cbbBaudrate.currentText(),
            "databits": self.cbbDatabits.currentText(),
            "stopbits": self.cbbStopbits.currentText(),
            "parity": self.cbbParity.currentText(),
            "flowcontrol": self.cbbFlowcontrol.currentText()
        }

        try:
            tulis_konfigurasi(data)
            QtWidgets.QMessageBox.information(self, "Sukses", "Konfigurasi berhasil disimpan.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Gagal", f"Gagal menyimpan konfigurasi:\n{e}")

    def load_record(self):
        config = baca_konfigurasi()
        if not config:
            return

        self.edNama.setText(config.get("nama_perusahaan", ""))
        self.txtedAlamat.setPlainText(config.get("alamat", ""))
        self.edTelepon.setText(config.get("telepon", ""))
        self.cbbComport.setCurrentText(config.get("comport", ""))
        self.cbbBaudrate.setCurrentText(config.get("baudrate", BAUDRATES[0]))
        self.cbbDatabits.setCurrentText(config.get("databits", DATABITS[0]))
        self.cbbStopbits.setCurrentText(config.get("stopbits", STOPBITS[0]))
        self.cbbParity.setCurrentText(config.get("parity", PARITY[0]))
        self.cbbFlowcontrol.setCurrentText(config.get("flowcontrol", FLOWCONTROL[0]))
