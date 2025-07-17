import hashlib
from modules.config.config import TABLES
from modules.helper.db import execute_query
from PyQt5 import QtWidgets
from modules.helper import auth
from .form_ganti_password import Ui_Form


class GantiPasswordMain(QtWidgets.QWidget, Ui_Form):
    # Constructor
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connect_signals()
        self.reset_input()

    def reset_input(self):
        self.edPassword.setText("")
        self.edConfirmPassword.setText("")
        self.edPassword.setFocus()

    def connect_signals(self):
        self.btnSave.clicked.connect(self.save_record)
        self.btnClear.clicked.connect(self.reset_input)

    def save_record(self):
        password = self.edPassword.text().strip()
        confirmpassword = self.edConfirmPassword.text().strip()

        if password == confirmpassword:
            id_record = auth.get_userid()
            password = hashlib.sha256(self.edPassword.text().encode()).hexdigest()
            execute_query(f"""
                UPDATE {TABLES['TblUser']}
                SET password = ?
                WHERE id = ?
            """, (password, id_record))
            self.reset_input()
            QtWidgets.QMessageBox.information(self, "Ganti Password", "Sukses")
        else:
            QtWidgets.QMessageBox.warning(self, "Ganti Password", "Gagal !!!")
