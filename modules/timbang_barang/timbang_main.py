from PyQt5 import QtWidgets
from .form_timbang import Ui_Form
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from modules.config.config import REGEX_BERAT_TEMPLATE  # ambil mask dari config kamu
from modules.helper.fontsetup import SetupEdLineFont
from modules.utils.format_utils import  apply_thousand_separator
from PyQt5.QtWidgets import QCompleter, QMessageBox
from modules.helper.db import get_nama_barang_aktif, get_nama_pemasok_pelanggan_aktif, \
    get_transaksi_by_no_tiket, get_nama_barang_by_id, get_nama_pemasok_pelanggan_id, fetch_transaksi, count_transaksi
from modules.helper.report_table_model import ReportTableModel
from modules.helper.db import get_daftar_no_tiket
from modules.helper.regex_serial_parser import RegexSerialParser
from modules.helper.transaction_handler import validasi_transaksi, proses_timbang_masuk, proses_timbang_keluar
from modules.helper.serial_manager import SerialManager
from modules.utils.switch_mode_widget import SwitchModeWidget



class TimbangMain(QtWidgets.QWidget, Ui_Form):
    com_status_changed = pyqtSignal(str, bool)
    weight_received = pyqtSignal(str)  # sinyal kirim data ke UI-thread

    # Constructor
    def __init__(self, current_user, current_user_level):
        super().__init__()
        self.current_user = current_user
        self.current_user_level = current_user_level
        self.setupUi(self)
        self.init_state_variables()
        self.init_number_formatting()
        self.init_field_fonts()
        self.init_readonly_fields()
        # Thread for serial data
        self.weight_received.connect(self.update_weight_display)
        # Format for serial data
        self.parser = RegexSerialParser(REGEX_BERAT_TEMPLATE)
        self.init_switch_controls()
        self.connect_signals()
        self.init_completer()
        self.load_data_transaksi()
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)  # jeda 300ms
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._lakukan_pencarian)

        # Hubungkan ke edSearch
        self.edSearch.textChanged.connect(self._jadwalkan_pencarian)

    # Init Variable State
    def init_state_variables(self):
        self.last_raw_data = ""
        self.serial_thread = None
        self.serial_worker = None
        self.timbang1 = 0
        self.timbang2 = 0
        self.netto = 0

    # Init Component Formating Number
    def init_number_formatting(self):
        apply_thousand_separator(self.edCurrentWeight)
        apply_thousand_separator(self.edTimbang1)
        apply_thousand_separator(self.edTimbang2)
        apply_thousand_separator(self.edNetto)

    # Init Font in Component
    def init_field_fonts(self):
        SetupEdLineFont(self.edCurrentWeight, Qt.AlignCenter, 27)
        SetupEdLineFont(self.edNoTiket, Qt.AlignCenter, 20)
        SetupEdLineFont(self.edTimbang1, Qt.AlignCenter, 20)
        SetupEdLineFont(self.edTimbang2, Qt.AlignCenter, 20)
        SetupEdLineFont(self.edNetto, Qt.AlignCenter, 20)

    # Init ReadOnly Mode
    def init_readonly_fields(self):
        self.edTimbang1.setReadOnly(True)
        self.edTimbang2.setReadOnly(True)
        self.edNetto.setReadOnly(True)
        readonly_style = """
                    QLineEdit[readOnly="true"] {
                        background-color: #f0f0f0;
                        color: #000;
                        font-weight: bold;
                    }
                """

        self.edTimbang1.setStyleSheet(readonly_style)
        self.edTimbang2.setStyleSheet(readonly_style)
        self.edNetto.setStyleSheet(readonly_style)

    # Init SwitchControl
    def init_switch_controls(self):
        self.modeTransaksi = "pemasok"
        switch_transaksi = SwitchModeWidget( on_text="Pemasok", off_text="Pembeli", start_flag=False,
            callback=self.on_toggle_transaksi
        )
        switch_transaksi.label.setStyleSheet("text-align: left;font-weight: bold; font-size: 10pt; color: #000;padding-left: 4px;")
        self.layoutModeSwitch.layout().addWidget(switch_transaksi)

        switch_com = SwitchModeWidget( on_text="Port : Open", off_text="Port : Closed", start_flag=False,
            callback=self.on_toggle_comport
        )
        switch_com.label.setStyleSheet("text-align: left;font-weight: bold; font-size: 10pt; color: #000;padding-left: 4px;")
        self.layoutModeComport.layout().addWidget(switch_com)

    # Init Signal
    def connect_signals(self):
        self.btnTimbang.clicked.connect(self.handle_timbang)
        self.btnClear.clicked.connect(self.reset_timbangan)
        self.btnSave.clicked.connect(self.save_record)
        self.btnLoadTiket.clicked.connect(self.try_load_transaksi_tiket)

    # Auto-completion untuk barang, pemasok, pelanggan, notiket
    def init_completer(self):
        self.edNamaBarang.setCompleter(self.refresh_completer_edt(get_nama_barang_aktif()))
        self.edPemasok.setCompleter(self.refresh_completer_edt(get_nama_pemasok_pelanggan_aktif(self.modeTransaksi)))
        self.edNoTiket.setCompleter(self.refresh_completer_edt(get_daftar_no_tiket(self.modeTransaksi)))

    def on_toggle_transaksi(self, checked):
        self.modeTransaksi = "pelanggan" if checked else "pemasok"

        self.lbl_pemasok_pelanggan.setText(self.modeTransaksi.capitalize())
        self.set_tipe_transaksi(self.modeTransaksi)

        # Ganti data untuk auto-completer pemasok/pelanggan
        completer = QCompleter(get_nama_pemasok_pelanggan_aktif(self.modeTransaksi))
        completer.setCaseSensitivity(False)
        self.edPemasok.setCompleter(completer)

        # 🔁 Update callback SmartTableModel agar data sesuai mode terbaru
        if hasattr(self, 'model_transaksi'):
            self.model_transaksi.set_fetch_callback(
                lambda offset, limit, search, sort_col, sort_order:
                fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order)
            )
            self.model_transaksi.set_count_callback(
                lambda search: count_transaksi(self.modeTransaksi, search)
            )
            self.model_transaksi.set_search_term("")  # Optional: reset pencarian
            self.model_transaksi.reload()

    def handle_com_status(self, port, status):
        self.com_status_changed.emit(port, True) if status else self.com_status_changed.emit("", False)

    def on_toggle_comport(self, checked):
        if checked:
            self.serial_manager = SerialManager()
            self.serial_manager.data_received.connect(self.update_weight_display)
            self.serial_manager.status_changed.connect(self.handle_com_status)
            self.serial_manager.start()
        else:
            if self.serial_manager:
                self.serial_manager.stop()

            self.edCurrentWeight.setText("")

    def update_weight_display(self, data):
        self.last_raw_data = data

        if self.parser.validate(data):
            weight = self.parser.extract_weight(data)
            unit = self.parser.extract_unit(data)
            if weight is not None:
                display = f"{self.parser.format_weight_locale(weight)}"
                self.edCurrentWeight.setText(display)
            else:
                print(f"[IGNORED] Format tidak sesuai mask: {data}")
                self.edCurrentWeight.setText("0.0")

    def show_serial_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Serial Error", message)

    def set_tipe_transaksi(self, mode):
        print(f"Mode transaksi diset ke: {mode}")

    def handle_timbang(self):
        if not self.last_raw_data:
            QtWidgets.QMessageBox.warning(self, "Data Timbang", "Belum ada data timbangan.")
            return

        weight = self.parser.extract_weight(self.last_raw_data)
        if weight is None:
            QtWidgets.QMessageBox.warning(self, "Format Error", "Data tidak sesuai format mask.")
            return

        if not self.edTimbang1.text():
            self.edTimbang1.setText(f"{weight:.1f}")
            self.timbang1 = weight
        elif not self.edTimbang2.text():
            self.edTimbang2.setText(f"{weight:.1f}")
            self.timbang2 = weight
            self.calc_netto()
        else:
            QtWidgets.QMessageBox.information(self, "Info", "Kedua timbang sudah terisi. Tekan Reset untuk mengulang.")

        self.perbarui_status_tombol_simpan()

    def reset_timbangan(self):
        self.edNoTiket.setText("")
        self.edTimbang1.setText("")
        self.edTimbang2.setText("")
        self.edNetto.setText("")
        self.edPemasok.setText("")
        self.edNamaBarang.setText("")
        self.edNomorPolisi.setText("")
        self.edNamaSopir.setText("")
        self.edNomorPO.setText("")
        self.txtedKeterangan.setPlainText("")
        self.timbang2 = 0
        self.timbang1 = 0
        self.netto = 0
        self.form_readonly_mode(False)

    def calc_netto(self):
        self.netto = abs(self.timbang1 - self.timbang2)
        self.edNetto.setText(f"{self.netto:.1f}")

    def simpan_transaksi(self):
        no_tiket = self.edNoTiket.text().strip()
        error = validasi_transaksi(no_tiket, self.timbang1, self.timbang2)
        if error:
            QMessageBox.warning(self, "Validasi", error)
            return

        form_data = {
            'pemasok': self.edPemasok.text().strip(),
            'barang': self.edNamaBarang.text().strip(),
            'nopol': self.edNomorPolisi.text().strip(),
            'nopo': self.edNomorPO.text().strip(),
            'sopir': self.edNamaSopir.text().strip(),
            'keterangan': self.txtedKeterangan.toPlainText().strip(),
            'timbang1': self.timbang1,
            'timbang2': self.timbang2
        }

        updated = proses_timbang_keluar(self.modeTransaksi, no_tiket, form_data,
                                        self.current_user, form_data['keterangan'], self.timbang2)
        if updated:
            QMessageBox.information(self, "Berhasil", "Timbang kedua diperbarui.")
            return

        inserted = proses_timbang_masuk(self.modeTransaksi, no_tiket, form_data, self.current_user)
        if inserted:
            QMessageBox.information(self, "Berhasil", "Timbang masuk disimpan.")
            if self.timbang1 > 0 and self.timbang2 > 0:
                self.form_readonly_mode(True)
        else:
            QMessageBox.warning(self, "Validasi", "Pemasok atau Barang tidak ditemukan.")

    def save_record(self):
        self.simpan_transaksi()

    def load_transaksi_untuk_timbang_kedua(self, no_tiket):
        data = get_transaksi_by_no_tiket(self.modeTransaksi, no_tiket)
        if not data:
            QtWidgets.QMessageBox.warning(self, "Data Tidak Ditemukan", f"Tiket '{no_tiket}' tidak ditemukan.")
            return

        (
            no_tiket, no_polisi, no_po_do,
            id_barang, nama_sopir,
            gross, tare, netto,
            tanggal_masuk, keterangan,
            id_pemasok, id_pelanggan,
            timbang1, timbang2
        ) = data

        self.edNoTiket.setText(no_tiket)
        self.edNomorPolisi.setText(no_polisi)
        self.edNomorPO.setText(no_po_do)
        self.edNamaBarang.setText(get_nama_barang_by_id(id_barang))  # kamu bisa bikin fungsi lookup nama
        self.edNamaSopir.setText(nama_sopir)
        self.txtedKeterangan.setPlainText(keterangan or "")
        self.timbang1 = timbang1
        self.timbang2 = timbang2
        self.calc_netto()
        self.edTimbang1.setText(f"{timbang1:.1f}" if timbang1 else "")
        self.edTimbang2.setText(f"{timbang2:.1f}" if timbang2 else "")

    def refresh_completer_edt(self, data):
        completer_value = QCompleter(data)
        completer_value.setCaseSensitivity(False)
        return completer_value

    def try_load_transaksi_tiket(self):
        no_tiket = self.edNoTiket.text().strip()
        if no_tiket:
            self.load_transaksi_untuk_timbang_kedua(no_tiket)

    def load_transaksi_untuk_timbang_kedua(self, no_tiket):
        data = get_transaksi_by_no_tiket(self.modeTransaksi, no_tiket)
        if not data:
            QtWidgets.QMessageBox.warning(self, "Data Tidak Ditemukan", f"No Tiket '{no_tiket}' tidak ditemukan.")
            return

        (
            no_tiket, no_polisi, no_po_do,
            id_barang, nama_sopir,
            gross, tare, netto,
            tanggal_masuk, keterangan,
            id_pemasok_pelanggan,
            timbang1, timbang2
        ) = data

        self.edNoTiket.setText(no_tiket)
        self.edNomorPolisi.setText(no_polisi)
        self.edNomorPO.setText(no_po_do)
        self.edNamaSopir.setText(nama_sopir)
        self.txtedKeterangan.setPlainText(keterangan or "")
        self.nama_pemasok_pelanggan = get_nama_pemasok_pelanggan_id(self.modeTransaksi, id_pemasok_pelanggan)
        self.edPemasok.setText(self.nama_pemasok_pelanggan)

        self.edNamaBarang.setText(get_nama_barang_by_id(id_barang))
        self.timbang1 = timbang1 or 0
        self.timbang2 = timbang2 or 0
        self.edTimbang1.setText(f"{self.timbang1:.1f}" if self.timbang1 else "")
        self.edTimbang2.setText(f"{self.timbang2:.1f}" if self.timbang2 else "")
        self.calc_netto()

    def form_readonly_mode(self, mode):
        self.edTimbang1.setReadOnly(mode)
        self.edTimbang2.setReadOnly(mode)
        self.edCurrentWeight.setReadOnly(mode)
        self.edNoTiket.setReadOnly(mode)
        self.edPemasok.setReadOnly(mode)
        self.edNamaBarang.setReadOnly(mode)
        self.edNomorPolisi.setReadOnly(mode)
        self.edNomorPO.setReadOnly(mode)
        self.edNamaSopir.setReadOnly(mode)
        self.txtedKeterangan.setReadOnly(mode)
        self.btnSave.setEnabled(mode)

    def perbarui_status_tombol_simpan(self):
        if self.timbang1 > 0 and self.timbang2 > 0 and self.timbang1 != self.timbang2:
            # Timbang kedua selesai ➝ aktifkan Save
            self.btnSave.setEnabled(True)
        elif self.timbang1 > 0 and self.timbang2 == 0:
            # Baru timbang pertama ➝ Save tetap diizinkan
            self.btnSave.setEnabled(True)
        else:
            self.btnSave.setEnabled(False)

    def load_data_transaksi(self):
        self.model_transaksi = ReportTableModel(
            headers=["No Tiket", "No Polisi", "No DO", "Nama Sopir", "Timbang ke-1", "Timbang ke-2", "Gross", "Tare",
                     "Netto"],
            fetch_callback=lambda offset, limit, search, sort_col, sort_order:
            fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order),
            count_callback=lambda search:
            count_transaksi(self.modeTransaksi, search)
        )

        self.tableView.setModel(self.model_transaksi)

        self.tableView.verticalScrollBar().valueChanged.connect(lambda _: self.model_transaksi.fetchMore())
        self.tableView.setSortingEnabled(True)

        # 🔁 Search field terhubung ke debounce
        self.edSearch.textChanged.connect(self._jadwalkan_pencarian)

    def _jadwalkan_pencarian(self, teks):
        self.search_term = teks
        self.search_timer.start()  # reset timer setiap ngetik


    def _lakukan_pencarian(self):
        if hasattr(self, 'model_transaksi'):
            self.model_transaksi.set_search_term(self.search_term)

