import hashlib
from modules.helper import auth  # jika kamu sudah pakai modul auth seperti sebelumnya
from modules.main_window.window_main import MainWindow  # asumsi ini window utama kamu
from PyQt5 import QtWidgets, QtCore
from modules.Login.form_login import Ui_Form
from modules.helper.db import execute_select


class LoginMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnLogin.setDefault(True)
        self.connect_signals()
        self.clear_form()
        self.edUsername.setFocus()
        self.DeveloperMode()

    def connect_signals(self):
        self.btnLogin.clicked.connect(self.login)
        self.btnExit.clicked.connect(self.close)

    def clear_form(self):
        self.edUsername.setText("")
        self.edPassword.setText("")

    def login(self):
        username = self.edUsername.text().strip()
        password = self.edPassword.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Input Kosong", "Harap isi username dan password.")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        user = execute_select(
            "SELECT id, username, level FROM db_master_user WHERE username = ? AND password = ? AND status = 1",
            (username, hashed)
        )

        if user:
            # Login sukses
            auth.set_user(user[0][0], username, user[0][2])  # set current_user dan level
            self.window_main = MainWindow()
            self.window_main.show()
            self.close()
        else:
            QtWidgets.QMessageBox.critical(self, "Login Gagal", "Username atau password salah.")

    def DeveloperMode(self):
        self.edUsername.setText("ferry")
        self.edPassword.setText("ferry")
        self.btnLogin.setFocus()