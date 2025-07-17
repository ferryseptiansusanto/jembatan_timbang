import hashlib
from modules.config.config import TABLES
from modules.helper.db import execute_query
from PyQt5 import QtWidgets
from .form_ganti_password import Ui_Form


class GantiPasswordMain(QtWidgets.QWidget, Ui_Form):
    # Constructor
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.setupUi(self)
        self.id_record = None
        self.connect_signals()
        self.reset_input()

    def reset_input(self):
        self.id_record = None
        self.edPassword.setText("")
        self.edConfirmPassword.setText("")
        self.edPassword.setFocus()

    def connect_signals(self):
        self.btnSave.clicked.connect(self.save_record)
        self.btnClear.clicked.connect(self.reset_input)

    def save_record(self):

        id_record = self.id_record
        password = hashlib.sha256(self.edPassword.text().encode()).hexdigest()
        level = self.cbbLevel.currentText()
        nama = self.edName.text()
        status = 1 if self.cbActive.isChecked() else 0
        execute_query(f"""
            UPDATE {TABLES['TblUser']}
            SET password = ?
            WHERE id = ?
        """, (  password, id_record))
        QtWidgets.QMessageBox.information(self, "Berhasil", "Data user diperbarui.")
        self.reset_input()
