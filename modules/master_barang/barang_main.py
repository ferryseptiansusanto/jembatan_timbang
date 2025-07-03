import sqlite3
import datetime
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtSql import QSqlTableModel
from .form_barang import Ui_Form  # pastikan form_user.py ada di folder yang sama
from modules.helper.db import execute_query, init_qt_connection
from qtviewmodels.checkbox_model import CheckBoxSqlTableModel
from modules.config.config import TABLES


class BarangMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.setupUi(self)
        self.qt_db = init_qt_connection()
        self.id_record = None
        self.setup_model()
        self.connect_signals()
        self.clear_form()
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.setWindowTitle(f"Master Barang - Login oleh: {self.current_user}")

    def setup_model(self):
        self.model = QSqlTableModel()
        self.model = CheckBoxSqlTableModel(checkbox_column=7)
        self.model.setTable(TABLES["TblBarang"])
        self.model.select()
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "Nama Barang")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "Kategori")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "Dibuat Tanggal")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "Diubah Tanggal")
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, "User Pembuat")
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, "User Pengubah")
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, "Aktif")
        self.tvBarang.setModel(self.model)
        QtCore.QTimer.singleShot(0, lambda: self.tvBarang.selectionModel().selectionChanged.connect(
            self.fill_form_from_table))
        self.tvBarang.hideColumn(0)  # Sembunyikan kolom ID
        self.tvBarang.hideColumn(3)  # Sembunyikan kolom created_date
        self.tvBarang.hideColumn(4)  # Sembunyikan kolom modified_date
        self.tvBarang.hideColumn(5)  # Sembunyikan kolom created_by
        self.tvBarang.hideColumn(6)  # Sembunyikan kolom modified_by

    def refresh_model(self):
        self.model.select()
        self.tvBarang.clearSelection()

    def connect_signals(self):
        self.btnSave.clicked.connect(self.save_record)
        self.btnDelete.clicked.connect(self.delete_record)
        self.btnClear.clicked.connect(self.clear_form)

    def fill_form_from_table(self, selected, deselected):
        indexes = self.tvBarang.selectionModel().selectedRows()
        if indexes:
            row = indexes[0].row()
            record = self.model.record(row)
            self.id_record = record.value("id")
            self.edNamaBarang.setText(record.value("namabarang"))
            self.edKategori.setText(record.value("kategori"))
            self.cbActive.setChecked(record.value("active") == 1)
            self.set_mode()

    def save_record(self):
        if self.id_record is None:
            self.add_record()
        else:
            self.edit_record()

    def add_record(self):
        namabarang = self.edNamaBarang.text()
        kategori = self.edKategori.text()
        created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        modified_date = None
        created_by = self.current_user
        modified_by = None
        active = 1 if self.cbActive.isChecked() else 0

        if not namabarang or not kategori:
            QtWidgets.QMessageBox.warning(self, "Input tidak lengkap", "Isi semua field wajib.")
            return

        try:
            execute_query(f"""
                INSERT INTO {TABLES['TblBarang']} (namabarang, kategori, created_date, modified_date, created_by
                , modified_by, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (namabarang, kategori, created_date, modified_date, created_by, modified_by, active))

            QtWidgets.QMessageBox.information(self, "Sukses", f"User '{namabarang}' berhasil ditambahkan.")
            self.clear_form()
            self.refresh_model()

        except sqlite3.IntegrityError as e:
            QtWidgets.QMessageBox.critical(self, "Gagal", f"Username '{namabarang}' sudah digunakan.")

    def edit_record(self):
        id_record = self.id_record
        namabarang = self.edNamaBarang.text()
        kategori = self.edKategori.text()
        modified_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        modified_by = self.current_user
        active = 1 if self.cbActive.isChecked() else 0

        execute_query(f"""
            UPDATE {TABLES['TblBarang']}
            SET namabarang=?, kategori=?, modified_date=?, modified_by=?, active=?
            WHERE id = ?
        """, (namabarang, kategori, modified_date, modified_by, active, id_record))

        QtWidgets.QMessageBox.information(self, "Berhasil", "Data barang diperbarui.")
        self.clear_form()
        self.refresh_model()

    def delete_record(self):
        # Cek hak akses
        if self.current_user_level.lower() != "administrator":
            QtWidgets.QMessageBox.warning(
                self,
                "Akses Ditolak",
                "Hanya user dengan level 'administrator' yang dapat menghapus data."
            )
            return

        if self.id_record is None:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Pilih data yang ingin dihapus terlebih dahulu.")
            return

        # Konfirmasi sebelum hapus
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Yakin ingin menghapus data ini?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            execute_query(f"DELETE FROM {TABLES['TblBarang']} WHERE id = ?", (self.id_record,))
            QtWidgets.QMessageBox.information(self, "Sukses", "Data berhasil dihapus.")
            self.clear_form()
            self.refresh_model()

    def clear_form(self):
        self.id_record = None
        self.edNamaBarang.clear()
        self.edKategori.clear()
        self.cbActive.setChecked(True)
        self.set_mode()
        self.tvBarang.clearSelection()

    def set_mode(self):
        if self.id_record is None:
            self.btnSave.setText("Add")
        else:
            self.btnSave.setText("Edit")
