import os

from PyQt5 import QtWidgets, QtCore
from .form_report import Ui_Form
from .report_handler import ReportHandler
from modules.helper.db import fetch_transaksi, count_transaksi
from modules.helper.report_table_model import ReportTableModel
from modules.helper.konversidatetime import get_range_timestamp
from modules.utils.pdf_preview import PDFReportPreview

from modules.config.company_profile import CompanyProfile
from modules.utils.pdf_preview_config import PDFReportPreviewConfigurable


class ReportMain(QtWidgets.QWidget, Ui_Form):
    def __init__(self, current_user, current_user_level, mode_transaksi="pelanggan"):
        super().__init__()
        self.setupUi(self)

        self.current_user = current_user
        self.current_user_level = current_user_level
        self.mode_transaksi = mode_transaksi.lower()
        self.setWindowTitle(f"Laporan Transaksi - {self.mode_transaksi.capitalize()}")

        self.company = CompanyProfile()

        # Optional: tetap pakai ReportHandler untuk fitur export nanti
        self.report = ReportHandler(mode_transaksi=self.mode_transaksi)

        # Header kolom tabel
        self.headers = [
            "Tiket", "Nopol", "PO/DO",
            "Nama Pemasok" if self.mode_transaksi == "pemasok" else "Nama Pelanggan",
            "Barang", "Sopir", "Gross", "Tare", "Netto",
            "Masuk", "Keluar", "Keterangan"
        ]

        self.connect_signals()
        self.clear_form()
        self.init_table()

    def connect_signals(self):
        self.btnSearch.clicked.connect(self.search_data)
        self.btnExportPdf.clicked.connect(self.pdf_data)
        self.btnExportExcel.clicked.connect(self.excel_data)

    def clear_form(self):
        self.edSearch.clear()
        self.dateStart.setDate(QtCore.QDate.currentDate().addDays(-7))
        self.dateEnd.setDate(QtCore.QDate.currentDate())

    def init_table(self):
        self.model = ReportTableModel(
            headers=self.headers,
            fetch_callback=self.fetch_data,
            count_callback=self.count_data,
            batch_size=100
        )

        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().sectionClicked.connect(self.model.sort)

    def search_data(self):
        self.model.set_search_term(self.edSearch.text().strip())
        self.model.reload()

    def fetch_data(self, offset, limit, search, sort_col, sort_order):
        ts_start, ts_end = get_range_timestamp(self.dateStart.date(), self.dateEnd.date())

        if ts_start > ts_end:
            ts_start, ts_end = ts_end, ts_start

        return fetch_transaksi(
            self.mode_transaksi,
            offset,
            limit,
            search,
            sort_col,
            sort_order,
            ts_start,
            ts_end
        )

    def count_data(self, search):


        if not self.dateStart.date().isValid() or not self.dateEnd.date().isValid():
            QtWidgets.QMessageBox.warning(self, "Tanggal Tidak Valid", "Isi rentang tanggal dengan benar.")
            return

        ts_start, ts_end = get_range_timestamp(self.dateStart.date(), self.dateEnd.date())

        if ts_start > ts_end:
            ts_start, ts_end = ts_end, ts_start

        return count_transaksi(
            self.mode_transaksi,
            search,
            ts_start,
            ts_end
        )

    def setConfigPreview(self):
        supplier_key = "Nama Pemasok" if self.mode_transaksi == "pemasok" else "Nama Pelanggan"
        fields_config = [
            {"key": "Masuk", "alias": "Tanggal", "width": 80, "is_ts": True},
            {"key": "Tiket", "alias": "No Tiket", "width": 60},
            {"key": "PO/DO", "alias": "PO/DO", "width": 60},
            {"key": "Nopol", "alias": "No Polisi", "width": 50},
            {"key": supplier_key, "alias": "Nama Supplier", "width": 80},
            {"key": "Barang", "alias": "Nama Barang", "width": 120},
            {"key": "Gross", "alias": "Gross (kg)", "width": 60, "numeric": True},
            {"key": "Tare", "alias": "Tare (kg)", "width": 60, "numeric": True},
            {"key": "Netto", "alias": "Netto (kg)", "width": 60, "numeric": True},
            {"key": "Sopir", "alias": "Nama Sopir", "width": 60},
            {"key": "Keterangan", "alias": "Keterangan", "width": 1, "split_row": True, "visible": False},
        ]
        # "Tiket", "Nopol", "PO/DO",
        # "Nama Pemasok" if self.mode_transaksi == "pemasok" else "Nama Pelanggan",
        # "Barang", "Sopir", "Gross", "Tare", "Netto",
        # "Masuk", "Keluar", "Keterangan"
        return fields_config

    def pdf_data(self):
        preview = PDFReportPreviewConfigurable(
            title="Laporan Timbang",
            subtitle=f"{self.company.nama}\nPeriode: {self.dateStart.text()} s.d. {self.dateEnd.text()}",
            landscape_mode=True
        )

        fields_config = self.setConfigPreview()

        preview.preview(
            self.model.headers,
            self.model.get_all_data(),
            fields_config,
            sort_by="Tiket",
            sort_reverse=False  # default: ascending
        )

    def excel_data(self):
        file_path = os.path.join(os.path.expanduser("~"), "Documents", "Laporan Timbang.xlsx")

        preview = PDFReportPreviewConfigurable(
            title="Laporan Timbang",
            subtitle=f"{self.company.nama}\nPeriode: {self.dateStart.text()} s.d. {self.dateEnd.text()}",
            landscape_mode=True
        )

        fields_config = self.setConfigPreview()

        preview.export_excel(
            headers=self.model.headers,
            data_rows=self.model.get_all_data(),
            fields_config=fields_config,
            file_path=file_path,
            sort_by="tanggal_masuk"
        )

