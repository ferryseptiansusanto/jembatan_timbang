from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QCompleter, QTableView, QPushButton, QLineEdit
from PyQt5.QtCore import QTimer, Qt,QSizeF
from .form_print import Ui_Form  # Form Qt Designer kamu
from customwidgets.switch_mode.switch_mode_form import SwitchButton
from modules.helper.db import fetch_transaksi, count_transaksi
from modules.helper.db import SmartTableModel
from modules.helper.xmlconfigurator import bacaslipxml, baca_konfigurasi
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter
from PyQt5.QtGui import QTextDocument
from modules.xml_editor import editor_template_slip
from modules.helper.konversidatetime import format_ts
import os
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView


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

        #headers = ["No Tiket", "No Polisi", "No DO", "Nama Sopir", "Timbang 1", "Timbang 2", "Gross", "Tare", "Netto"]
        # headers = [
        #     "No Tiket", "No Polisi", "No DO", "Nama Sopir",
        #     "Timbang 1", "Timbang 2", "Gross", "Tare", "Netto",
        #     "Supplier", "Barang", "Waktu In", "Waktu Out", "Keterangan"
        # ]

        self.model_transaksi = SmartTableModel(
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
        self.model_transaksi.reload()

    def _schedule_search(self, text):
        self.search_term = text
        self.search_timer.start()

    def _do_search(self):
        self.model_transaksi.set_search_term(self.search_term)

    # def handle_print(self):
    #     selected = self.tableView.selectionModel().selectedRows()
    #     if not selected:
    #         QtWidgets.QMessageBox.information(self, "Print", "Pilih baris yang ingin dicetak.")
    #         return
    #
    #     for index in selected:
    #         row_data = self.model_transaksi.data_rows[index.row()]
    #         print_data = dict(zip(self.model_transaksi.headers, row_data))
    #         # Gantikan ini dengan print preview atau QPrinter
    #         print(f"[CETAK] {print_data}")

    def handle_print(self):
        selected = self.tableView.selectionModel().selectedRows()
        if not selected:
            QtWidgets.QMessageBox.information(self, "Print", "Pilih baris yang ingin dicetak.")
            return

        row_data = self.model_transaksi.data_rows[selected[0].row()]
        data_dict = dict(zip(self.model_transaksi.headers, row_data))

        html_slip = self.render_template_slip(data_dict)
        self.cetak_dengan_template(html_slip)

    def cetak_dengan_template(self, html_str):
        self.page = QWebEnginePage(self)

        def on_print_finished(success):
            if success:
                print("[INFO] Slip berhasil dicetak.")
            else:
                print("[ERROR] Gagal mencetak slip.")

        def do_print():
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName("debug_slip.pdf")
            self.page.print(printer, on_print_finished)
            #
            # printer = QPrinter(QPrinter.HighResolution)
            # printer.setPaperSize(QSizeF(105, 300), QPrinter.Millimeter)
            # printer.setOrientation(QPrinter.Portrait)
            # printer.setFullPage(True)
            # self.page.print(printer, on_print_finished)

        # Load HTML, tunggu sampai selesai lalu cetak
        QTimer.singleShot(0, lambda: self.page.setHtml(html_str))

        self.page.loadFinished.connect(lambda ok: do_print() if ok else print("[ERROR] Gagal load HTML ke QWebEnginePage."))

    def render_template_slip(self, data_dict):
        #template_html = bacaslipxml()
        template_html = self.baca_template_html()

        if not template_html.strip():
            return "<p><b>Template kosong</b></p>"

        # 🔹 Ambil konfigurasi perusahaan
        config = baca_konfigurasi()

        placeholder_map = {
            "no_tiket": data_dict.get("No Tiket", ""),
            "no_polisi": data_dict.get("No Polisi", ""),
            "no_do": data_dict.get("No DO", ""),
            "nama_sopir": data_dict.get("Nama Sopir", ""),
            "timbang1": data_dict.get("Timbang 1", ""),
            "timbang2": data_dict.get("Timbang 2", ""),
            "gross": data_dict.get("Gross", ""),
            "tare": data_dict.get("Tare", ""),
            "netto": data_dict.get("Netto", ""),
            "supplier": data_dict.get("Supplier", ""),
            "barang": data_dict.get("Barang", ""),
            "tanggal_masuk": format_ts(data_dict.get("Tanggal Masuk", 0)),
            "tanggal_keluar": format_ts(data_dict.get("Tanggal Keluar", 0)),
            "keterangan": data_dict.get("Keterangan", ""),
            "user": self.current_user,
            "nama_perusahaan": config.get("nama_perusahaan", ""),
            "alamat": config.get("alamat", ""),
            "telepon": config.get("telepon", "")
        }

        for key, value in placeholder_map.items():
            template_html = template_html.replace(f"{{{{{key}}}}}", str(value))

        return template_html

    def baca_template_html(self, filepath=None):
        if filepath is None:
            # Path relatif dari root project
            filepath = os.path.join("resources", "layout", "template_slip_html.html")

        try:
            with open(filepath, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print("[ERROR baca_template_html]:", e)
            return ""

    def preview_slip(self, html_str):
        view = QWebEngineView()
        view.setHtml(html_str)
        view.setWindowTitle("Preview Slip Timbang")
        view.resize(700, 1000)
        view.show()

