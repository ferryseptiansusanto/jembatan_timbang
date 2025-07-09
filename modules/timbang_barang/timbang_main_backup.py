from PyQt5 import QtWidgets
from .form_timbang import Ui_Form
from customwidgets.switch_mode.switch_mode_form import SwitchButton
from modules.helper.xmlconfigurator import baca_konfigurasi
from modules.config.config import BAUDRATES, DATABITS, STOPBITS, PARITY, FLOWCONTROL, map_parity, map_stopbits, \
    map_bytesize
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from modules.helper.serialworker import SerialWorker
from modules.config.config import REGEX_BERAT_TEMPLATE  # ambil mask dari config kamu
from modules.helper.fontsetup import SetupEdLineFont
from modules.utils.format_utils import  apply_thousand_separator
from PyQt5.QtWidgets import QCompleter
from modules.helper.db import get_nama_barang_aktif, get_nama_pemasok_pelanggan_aktif, \
    insert_transaksi_pemasok_pelanggan, is_no_tiket_exist, get_id_pemasok_pelanggan_by_nama, \
    get_id_barang_by_nama, get_transaksi_by_no_tiket, get_nama_barang_by_id, get_nama_pemasok_pelanggan_id, \
    update_transaksi_timbang_kedua, fetch_transaksi, count_transaksi
from modules.helper.report_table_model import ReportTableModel
from modules.helper.db import get_daftar_no_tiket
from modules.helper.regex_serial_parser import RegexSerialParser
from time import time
from modules.helper.transaction_handler import validasi_transaksi, proses_timbang_masuk, proses_timbang_keluar



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
        # Switch Transaksi
        self.switchTransaksi = SwitchButton()
        self.switchTransaksi.setChecked(False)
        self.switchTransaksi.toggled.connect(self.on_toggle_transaksi)
        self.layoutModeSwitch.layout().addWidget(self.switchTransaksi)
        self.labelMode.setText("Mode Input : Pemasok")
        self.modeTransaksi = "pemasok"

        # Switch COM Port
        self.switchComPort = SwitchButton()
        self.switchComPort.setChecked(False)
        self.switchComPort.toggled.connect(self.on_toggle_comport)
        self.layoutModeComport.layout().addWidget(self.switchComPort)
        self.labelModeComport.setText("Com Port : Closed")
        self.portStatus = "closed"

    # Init Signal
    def connect_signals(self):
        self.btnTimbang.clicked.connect(self.handle_timbang)
        self.btnClear.clicked.connect(self.reset_timbangan)
        self.btnSave.clicked.connect(self.save_record)
        self.btnLoadTiket.clicked.connect(self.try_load_transaksi_tiket)

        # self.edNoTiket.editingFinished.connect(self.try_load_transaksi_tiket)

    # Auto-completion untuk barang, pemasok, pelanggan, notiket
    def init_completer(self):
        self.edNamaBarang.setCompleter(self.refresh_completer_edt(get_nama_barang_aktif()))
        self.edPemasok.setCompleter(self.refresh_completer_edt(get_nama_pemasok_pelanggan_aktif(self.modeTransaksi)))
        self.edNoTiket.setCompleter(self.refresh_completer_edt(get_daftar_no_tiket(self.modeTransaksi)))

    def on_toggle_transaksi(self, checked):
        self.modeTransaksi = "pelanggan" if checked else "pemasok"
        self.labelMode.setText(f"Mode Input : {self.modeTransaksi.capitalize()}")
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

    def on_toggle_comport(self, checked):

        if checked:
            config = baca_konfigurasi()
            if not config:
                return
            self.ComPort = config.get("comport", "")

            self.serial_worker = SerialWorker(
                port=self.ComPort,
                baudrate=config.get("baudrate", 9600),
                parity=map_parity(config.get("parity", "N")),
                stopbits=map_stopbits(config.get("stopbits", 1)),
                bytesize=map_bytesize(config.get("databits", 8))
            )

            self.serial_thread = QThread()
            self.serial_worker.moveToThread(self.serial_thread)

            self.serial_thread.started.connect(self.serial_worker.start)
            self.serial_worker.data_received.connect(self.update_weight_display)
            self.serial_worker.finished.connect(self.serial_thread.quit)
            self.serial_worker.finished.connect(self.serial_worker.deleteLater)
            self.serial_thread.finished.connect(self.serial_thread.deleteLater)

            self.serial_thread.start()
            self.labelModeComport.setText("COM Port : Open")
            self.com_status_changed.emit(self.ComPort, True)  # saat ON

        else:
            if self.serial_worker:
                self.serial_worker.stop()
            self.labelModeComport.setText("COM Port : Closed")
            self.com_status_changed.emit("", False)  # saat OFF
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

    def load_record(self):
        config = baca_konfigurasi()
        if not config:
            return

        self.comport = config.get("comport", "")
        self.baudrate = config.get("baudrate", BAUDRATES[0])
        self.databits = config.get("databits", DATABITS[0])
        self.stopbits = config.get("stopbits", STOPBITS[0])
        self.parity = config.get("parity", PARITY[0])
        self.flowcontrol = config.get("flowcontrol", FLOWCONTROL[0])

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
        if not no_tiket:
            QtWidgets.QMessageBox.warning(self, "Validasi", "No Tiket wajib diisi.")
            return

        if self.timbang1 == self.timbang2 and self.timbang1 > 0:
            QtWidgets.QMessageBox.warning(self, "Validasi Timbang", "Berat timbang 1 dan timbang 2 tidak boleh sama.")
            return

        existing = get_transaksi_by_no_tiket(self.modeTransaksi, no_tiket)

        nama_pemasok_pelanggan = self.edPemasok.text().strip()
        nama_barang = self.edNamaBarang.text().strip()

        id_pemasok_pelanggan = get_id_pemasok_pelanggan_by_nama(self.modeTransaksi, nama_pemasok_pelanggan)
        id_barang = get_id_barang_by_nama(nama_barang)

        if not id_pemasok_pelanggan or not id_barang:
            QtWidgets.QMessageBox.warning(self, "Validasi", "Pemasok atau Barang tidak ditemukan.")
            return

        id_field = "id_pemasok" if self.modeTransaksi == "pemasok" else "id_pelanggan"
        self.gross, self.tare = (self.timbang1, self.timbang2) if self.timbang1 > self.timbang2 else (
        self.timbang2, self.timbang1)
        self.is_timbang = 1 if self.timbang1 > 0 and self.timbang2 > 0 else 0

        if existing:
            if existing[-1] == 1:
                QtWidgets.QMessageBox.warning(self, "Duplikat",
                                              f"Transaksi dengan No Tiket '{no_tiket}' sudah selesai.")
                return

            # ⏩ Update Timbang Kedua
            data_update = {
                "gross": self.gross,
                "tare": self.tare,
                "netto": self.netto,
                "tanggal_keluar": int(time()),
                "keterangan": self.txtedKeterangan.toPlainText().strip(),
                "operator_timbang_keluar": self.current_user,
                "timbang2": self.timbang2,
                "is_timbang": self.is_timbang
            }

            update_transaksi_timbang_kedua(self.modeTransaksi, no_tiket, data_update)
            QtWidgets.QMessageBox.information(self, "Berhasil", "Timbang kedua berhasil diperbarui.")
        else:
            # ➕ Insert Timbang Pertama
            data_insert = {
                "no_tiket": no_tiket,
                "no_polisi": self.edNomorPolisi.text().strip(),
                "no_po_do": self.edNomorPO.text().strip(),
                id_field: id_pemasok_pelanggan,
                "id_barang": id_barang,
                "nama_sopir": self.edNamaSopir.text().strip(),
                "gross": self.gross,
                "tare": self.tare,
                "netto": self.netto,
                "tanggal_masuk": int(time()),
                "keterangan": self.txtedKeterangan.toPlainText().strip(),
                "operator_timbang_masuk": self.current_user,
                "is_timbang": self.is_timbang,
                "timbang1": self.timbang1,
                "timbang2": self.timbang2
            }

            insert_transaksi_pemasok_pelanggan(self.modeTransaksi, data_insert)
            QtWidgets.QMessageBox.information(self, "Berhasil", "Transaksi timbang masuk berhasil disimpan.")
            if self.is_timbang == 1:
                self.form_readonly_mode(True)

        #self.reset_timbangan()

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

