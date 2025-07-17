import sqlite3
import hashlib
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtSql import QSqlTableModel
from .form_user import Ui_Form
from modules.helper.db import execute_query, init_qt_connection
from qtviewmodels.checkbox_model import CheckBoxSqlTableModel
from modules.config.config import TABLES


class UserMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.setupUi(self)
        self.qt_db = init_qt_connection()
        self.id_record = None
        self.setup_combobox_level()
        self.setup_model()
        self.connect_signals()
        self.clear_form()
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.setWindowTitle(f"User Setting - Login oleh: {self.current_user}")

    def setup_model(self):
        self.model = QSqlTableModel()
        self.model = CheckBoxSqlTableModel(checkbox_column=4)
        self.model.setTable(TABLES["TblUser"])
        self.model.select()
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Username")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Password")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Level")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Status")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "Nama")
        self.tvUser.setModel(self.model)
        QtCore.QTimer.singleShot(0, lambda: self.tvUser.selectionModel().selectionChanged.connect(
            self.fill_form_from_table))
        self.tvUser.hideColumn(0)  # Sembunyikan kolom ID
        self.tvUser.hideColumn(2)  # Sembunyikan kolom password

    def refresh_model(self):
        self.model.select()
        self.tvUser.clearSelection()

    def connect_signals(self):
        self.btnSave.clicked.connect(self.save_user)
        self.btnDelete.clicked.connect(self.delete_user)
        self.btnClear.clicked.connect(self.clear_form)

    def fill_form_from_table(self, selected, deselected):
        indexes = self.tvUser.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            record = self.model.record(row)
            if record.value("level").lower() == "superadmin":
                QtWidgets.QMessageBox.critical(self, "Dilarang", "User 'superadmin' tidak dapat diubah.")
                self.clear_form()
                return

            self.id_record = record.value("id")
            self.edUsername.setText(record.value("username"))
            self.edName.setText(record.value("nama"))
            self.cbbLevel.setCurrentText(record.value("level"))
            self.cbActive.setChecked(record.value("status") == 1)
            self.set_mode()
            self.setup_password()

    def save_user(self):
        if self.id_record is None:
            self.add_user()
        else:
            self.edit_user()

    def add_user(self):
        username = self.edUsername.text()
        password = hashlib.sha256(self.edPassword.text().encode()).hexdigest()
        level = self.cbbLevel.currentText()
        nama = self.edName.text()
        status = 1 if self.cbActive.isChecked() else 0

        if not username or not password or not nama:
            QtWidgets.QMessageBox.warning(self, "Input tidak lengkap", "Isi semua field wajib.")
            return

        try:
            execute_query(f"""
                INSERT INTO {TABLES['TblUser']} (username, password, level, status, nama)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password, level, status, nama))
            QtWidgets.QMessageBox.information(self, "Sukses", f"User '{username}' berhasil ditambahkan.")
            self.clear_form()
            self.refresh_model()
        except sqlite3.IntegrityError as e:
            QtWidgets.QMessageBox.critical(self, "Gagal", f"Username '{username}' sudah digunakan.")

    def edit_user(self):
        id_record = self.id_record
        username = self.edUsername.text()
        # password = hashlib.sha256(self.edPassword.text().encode()).hexdigest()
        level = self.cbbLevel.currentText()
        nama = self.edName.text()
        status = 1 if self.cbActive.isChecked() else 0
        execute_query(f"""
            UPDATE {TABLES['TblUser']}
            SET username = ?, level = ?, status = ?, nama = ?
            WHERE id = ?
        """, (username, level, status, nama, id_record))
        QtWidgets.QMessageBox.information(self, "Berhasil", "Data user diperbarui.")
        self.clear_form()
        self.refresh_model()

    def delete_user(self):
        if self.current_user == self.edUsername.text():
            QtWidgets.QMessageBox.critical(self, "Ditolak", "Anda tidak dapat menghapus user yang sedang login.")
            return

        if self.current_user_level.lower() != "administrator":
            QtWidgets.QMessageBox.critical(self, "Akses Ditolak", "Hanya Administrator yang boleh menghapus user.")
            return

        if self.id_record is None:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Pilih user yang ingin dihapus.")
            return

        # Ambil level dari baris yang dipilih
        indexes = self.tvUser.selectionModel().selectedRows()
        if not indexes:
            return

        row = indexes[0].row()
        record = self.model.record(row)
        level = record.value("level")

        if level.lower() == "superadmin":
            QtWidgets.QMessageBox.warning(self, "Dilarang", "User 'SuperAdmin' tidak dapat dihapus.")
            return

        if level.lower() == "administrator":
            extra_confirm = QtWidgets.QMessageBox.question(
                self,
                "Konfirmasi Administrator",
                "User ini memiliki level 'Administrator'. Hapus tetap dilanjutkan?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if extra_confirm != QtWidgets.QMessageBox.Yes:
                return

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Yakin ingin menghapus user ini?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            execute_query(f"DELETE FROM {TABLES['TblUser']} WHERE id = ?", (self.id_record,))
            QtWidgets.QMessageBox.information(self, "Berhasil", "User berhasil dihapus.")
            self.clear_form()
            self.refresh_model()

    def clear_form(self):
        self.id_record = None
        self.edUsername.clear()
        self.edPassword.clear()
        self.edName.clear()
        self.cbActive.setChecked(True)
        self.cbbLevel.setCurrentIndex(0)
        self.set_mode()
        self.edPassword.setEnabled(True)
        self.tvUser.clearSelection()

    def set_mode(self):
        if self.id_record is None:
            self.btnSave.setText("Add")
        else:
            self.btnSave.setText("Edit")

    def setup_combobox_level(self):
        from PyQt5.QtGui import QStandardItemModel, QStandardItem

        model = QStandardItemModel()
        item_admin = QStandardItem("Administrator")
        item_user = QStandardItem("User Timbang")
        model.appendRow(item_admin)
        model.appendRow(item_user)
        item_superadmin = QStandardItem("SuperAdmin")
        item_superadmin.setEnabled(False)  # ← Tidak bisa dipilih
        model.appendRow(item_superadmin)
        self.cbbLevel.setModel(model)

    def setup_password(self):
        if self.edPassword.isEnabled():
            self.edPassword.setEnabled(False)
        else:
            self.edPassword.setEnabled(True)
