import tempfile, sys, subprocess, os, io
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from .form_print import Ui_Form  # Form Qt Designer kamu
from customwidgets.switch_mode.switch_mode_form import SwitchButton
from modules.helper.db import fetch_transaksi, count_transaksi
from modules.helper.report_table_model import ReportTableModel

from modules.print_transaksi.print_engine import cetak_slip
from modules.helper.messagebox_utils import show_info
from modules.config.company_profile import CompanyProfile

class PrintMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.setupUi(self)
        self.modeTransaksi = "pemasok"
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.init_components()
        self.connect_signals()
        self.load_data()
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)
        self.company = CompanyProfile()

    def init_components(self):
        # Setup tombol switch mode transaksi
        self.switchTransaksi = SwitchButton()
        self.layoutModeSwitch.layout().addWidget(self.switchTransaksi)
        self.labelMode.setText("Mode Transaksi: Pemasok")


        # Inisialisasi model
        headers = [
            "No Tiket", "No Polisi", "No DO", "Nama Sopir",
            "Timbang 1", "Timbang 2", "Gross", "Tare", "Netto",
            "Supplier", "Barang", "Tanggal Masuk", "Tanggal Keluar", "Keterangan"
        ]

        self.model_transaksi = ReportTableModel(
            headers=headers,
            fetch_callback=lambda offset, limit, search, sort_col, sort_order:
                fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order),
            count_callback=lambda search: count_transaksi(self.modeTransaksi, search)
        )
        self.tableView.setModel(self.model_transaksi)
        self.tableView.setSortingEnabled(True)
        self.tableView.verticalScrollBar().valueChanged.connect(lambda _: self.model_transaksi.fetchMore())

    def connect_signals(self):
        self.switchTransaksi.toggled.connect(self.on_toggle_mode)
        self.edSearch.textChanged.connect(self._schedule_search)
        self.btnPrint.clicked.connect(self.handle_print)

    def load_data(self):
        self.model_transaksi.reload()

    def on_toggle_mode(self, checked):
        self.modeTransaksi = "pelanggan" if checked else "pemasok"
        self.labelMode.setText(f"Mode Transaksi: {self.modeTransaksi.capitalize()}")

        self.model_transaksi.set_fetch_callback(
            lambda offset, limit, search, sort_col, sort_order:
            fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order)
        )
        self.model_transaksi.set_count_callback(
            lambda search: count_transaksi(self.modeTransaksi, search)
        )
        self.model_transaksi.set_search_term("")  # Optional: reset pencarian
        self.model_transaksi.reload()

    def _schedule_search(self, text):
        self.search_term = text
        self.search_timer.start()

    def _do_search(self):
        self.model_transaksi.set_search_term(self.search_term)

    def handle_print(self):
        selected = self.tableView.selectionModel().selectedRows()
        if not selected:
            show_info(self, "Pilih baris yang ingin dicetak.", "Print")
            return

        row_data = self.model_transaksi.data_rows[selected[0].row()]
        data_dict = dict(zip(self.model_transaksi.headers, row_data))
        cetak_slip(self, self.current_user, data_dict)

