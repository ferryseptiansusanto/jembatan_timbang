from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from .form_print import Ui_Form
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
        self.company = CompanyProfile()

        self.init_components()
        self.connect_signals()

        self.search_timer = QTimer()
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._do_search)

        self.load_data()

    # --- 1. Helper Methods (Menghilangkan Lambda Panjang & Berulang) ---
    def _fetch_transaksi_selesai(self, offset, limit, search, sort_col, sort_order):
        return fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order, status_timbang=1)

    def _count_transaksi_selesai(self, search):
        return count_transaksi(self.modeTransaksi, search, status_timbang=1)

    def init_components(self):
        self.switchTransaksi = SwitchButton()
        self.layoutModeSwitch.layout().addWidget(self.switchTransaksi)
        self.labelMode.setText("Mode Transaksi: Pemasok")

        # --- 2. Headers Disesuaikan Tepat 12 Kolom (Mencegah Crash Saat Print) ---
        headers = [
            "No Tiket", "No Polisi", "No PO/DO", "Nama Supplier",
            "Nama Barang", "Nama Sopir", "Gross", "Tare",
            "Netto", "Tanggal Masuk", "Tanggal Keluar", "Keterangan"
        ]

        self.model_transaksi = ReportTableModel(
            headers=headers,
            fetch_callback=self._fetch_transaksi_selesai,
            count_callback=self._count_transaksi_selesai
        )
        self.tableView.setModel(self.model_transaksi)
        self.tableView.setSortingEnabled(True)

    def connect_signals(self):
        self.switchTransaksi.toggled.connect(self.on_toggle_mode)
        self.edSearch.textChanged.connect(self._schedule_search)
        self.btnPrint.clicked.connect(self.handle_print)

    def load_data(self):
        self.model_transaksi.reload()

    # --- 3. Fungsi Toggle Bersih ---
    def on_toggle_mode(self, checked):
        self.modeTransaksi = "pelanggan" if checked else "pemasok"
        self.labelMode.setText(f"Mode Transaksi: {self.modeTransaksi.capitalize()}")

        # Update teks header di Index ke-3
        new_header = "Nama Pelanggan" if checked else "Nama Supplier"
        self.model_transaksi.headers[3] = new_header
        self.model_transaksi.layoutChanged.emit()

        # Karena menggunakan Helper Method, kita cukup mereset teks dan memanggil reload()
        self.model_transaksi.set_search_term("")
        self.model_transaksi.reload()

    def _schedule_search(self, text):
        self.search_term = text
        self.search_timer.start()

    def _do_search(self):
        self.model_transaksi.set_search_term(self.search_term)
        self.model_transaksi.reload()

    def handle_print(self):
        selected = self.tableView.selectionModel().selectedRows()
        if not selected:
            show_info(self, "Pilih baris yang ingin dicetak.", "Print")
            return

        row_data = self.model_transaksi.data_rows[selected[0].row()]

        # Mapping dict sekarang aman dan cocok antara struktur header dan output database
        data_dict = dict(zip(self.model_transaksi.headers, row_data))
        cetak_slip(self, self.current_user, data_dict)