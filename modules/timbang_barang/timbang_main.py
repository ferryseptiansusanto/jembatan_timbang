from PyQt5 import QtWidgets
from .form_timbang import Ui_Form
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from modules.config.config import REGEX_BERAT_TEMPLATE  # ambil mask dari config kamu
from modules.helper.fontsetup import SetupEdLineFont
from modules.utils.format_utils import  apply_thousand_separator
from PyQt5.QtWidgets import QCompleter, QMessageBox
from modules.helper.db import get_nama_barang_aktif, get_nama_pemasok_pelanggan_aktif, \
    get_transaksi_by_no_tiket, get_nama_barang_by_id, get_nama_pemasok_pelanggan_id, fetch_transaksi, \
    count_transaksi, get_daftar_no_tiket, generate_next_no_tiket, hapus_transaksi_by_tiket
from modules.helper.report_table_model import ReportTableModel
from modules.helper.regex_serial_parser import RegexSerialParser
from modules.helper.transaction_handler import validasi_transaksi, proses_timbang_masuk, proses_timbang_keluar
from modules.helper.serial_manager import SerialManager
from modules.utils.switch_mode_widget import SwitchModeWidget
from datetime import datetime

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
        # Siapkan timer pencarian sebelum connect_signals()
        self.search_timer = QTimer()
        self.search_timer.setInterval(300)  # jeda 300ms
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._lakukan_pencarian)

        self.init_switch_controls()
        self.connect_signals()
        self.init_completer()
        self.load_data_transaksi()
        self.set_new_ticket_number()


    # Init Variable State
    def init_state_variables(self):
        self.header_mitra = "Pemasok"
        self.last_raw_data = ""
        self.serial_thread = None
        self.serial_worker = None
        self.timbang1 = 0
        self.timbang2 = 0
        self.netto = 0
        self.is_tiket_loaded = False
        self.is_tiket_selesai = False
        self.edCurrentWeight.setReadOnly(True)

        # 1. Mengubah seleksi dari per-cell menjadi per-baris (Row)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # 2. Mencegah multiple select, hanya boleh pilih 1 baris
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

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
        switch_transaksi = SwitchModeWidget( on_text="Pembeli", off_text="Pemasok", start_flag=False,
            callback=self.on_toggle_transaksi
        )
        switch_transaksi.label.setStyleSheet("text-align: left;font-weight: bold; font-size: 10pt; color: #000;padding-left: 4px;")
        self.layoutModeSwitch.layout().addWidget(switch_transaksi)

        self.switch_com = SwitchModeWidget( on_text="Port : Open", off_text="Port : Closed", start_flag=False,
            callback=self.on_toggle_comport
        )
        self.switch_com.label.setStyleSheet("text-align: left;font-weight: bold; font-size: 10pt; color: #000;padding-left: 4px;")
        self.layoutModeComport.layout().addWidget(self.switch_com)

    # Init Signal
    def connect_signals(self):
        self.edSearch.textChanged.connect(self._jadwalkan_pencarian)
        self.btnTimbang.clicked.connect(self.handle_timbang)
        self.btnClear.clicked.connect(self.reset_timbangan)
        self.btnSave.clicked.connect(self.save_record)
        self.btnLoadTiket.clicked.connect(self.try_load_transaksi_tiket)
        # --- OPSI 1: Ketik tiket lalu tekan Enter ---
        self.edNoTiket.returnPressed.connect(self.try_load_transaksi_tiket)
        # --- OPSI 2: Double Click atau Tekan Enter di Tabel ---
        self.tableView.activated.connect(self.handle_tabel_dipilih)
        self.btnDelete.clicked.connect(self.handle_hapus)

    def showEvent(self, event):
        super().showEvent(event)

        # Pastikan ini hanya dieksekusi 1 kali saat aplikasi pertama kali dibuka
        if not hasattr(self, 'port_sudah_dibuka'):
            self.port_sudah_dibuka = True
            self.switch_com.switch.toggle()


    # Auto-completion untuk barang, pemasok, pelanggan, notiket
    def init_completer(self):
        self.edNamaBarang.setCompleter(self.refresh_completer_edt(get_nama_barang_aktif()))
        self.edPemasok.setCompleter(self.refresh_completer_edt(get_nama_pemasok_pelanggan_aktif(self.modeTransaksi)))
        self.edNoTiket.setCompleter(self.refresh_completer_edt(get_daftar_no_tiket(self.modeTransaksi)))

    def handle_com_status(self, port, status):
        # Gunakan QTimer agar perubahan UI antre dengan aman (tidak crash)
        if status:
            self.com_status_changed.emit(port, True)

            # Jika port terhubung (atau sukses reconnect), hijaukan switch & update label
            if hasattr(self, 'switch_com'):
                QTimer.singleShot(0, lambda: self.switch_com.set_checked(True))
        else:
            self.com_status_changed.emit("", False)

            # Jika port terputus (atau gagal connect), abukan switch & update label
            if hasattr(self, 'switch_com'):
                QTimer.singleShot(0, lambda: self.switch_com.set_checked(False))

    def on_toggle_comport(self, checked):
        try:
            if checked:
                # 1. BERSIHKAN THREAD LAMA (Jika ada) SEBELUM MEMBUAT BARU
                if hasattr(self, 'serial_manager') and self.serial_manager is not None:
                    if self.serial_manager.isRunning():
                        self.serial_manager.stop()
                    self.serial_manager.deleteLater()
                    self.serial_manager = None

                # 2. BUAT THREAD BARU
                self.serial_manager = SerialManager()

                from PyQt5.QtCore import Qt
                self.serial_manager.data_received.connect(self.update_weight_display, Qt.QueuedConnection)
                self.serial_manager.status_changed.connect(self.handle_com_status, Qt.QueuedConnection)

                self.serial_manager.start()
            else:
                # 3. MATIKAN DENGAN AMAN SAAT SWITCH OFF
                if hasattr(self, 'serial_manager') and self.serial_manager is not None:
                    self.serial_manager.stop()
                    # HAPUS BARIS INI -> self.serial_manager.wait(2000)
                    self.serial_manager.deleteLater()
                    self.serial_manager = None

                self.edCurrentWeight.setText("")

        except Exception as e:
            # Kembalikan switch jika terjadi error
            if hasattr(self, 'switch_com'):
                QTimer.singleShot(0, lambda: self.switch_com.set_checked(not checked))

            import traceback
            print(traceback.format_exc())

            # Buat teks error sesuai tindakan (buka atau tutup)
            aksi = "membuka" if checked else "menutup"
            QtWidgets.QMessageBox.critical(self, "Error Indikator",
                                           f"Gagal {aksi} koneksi ke jembatan timbang:\n{str(e)}")

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
        else:
            # 2. Beritahu kita jika regex menolaknya
            print(f"DEBUG: Data ditolak oleh Regex karena format tidak cocok!")

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

        if not self.is_tiket_loaded:
            # SKENARIO 1: TIKET BARU (Hanya boleh isi Timbang 1)
            if not self.edTimbang1.text():
                self.edTimbang1.setText(f"{weight:.1f}")
                self.timbang1 = weight
            else:
                # Jika tidak sengaja ter-klik 2x, munculkan peringatan ini dan blokir Timbang 2!
                QtWidgets.QMessageBox.warning(self, "Tahan Dulu",
                                              "Timbang 1 sudah terisi!\nSilakan klik SIMPAN terlebih dahulu untuk truk ini.")
        else:
            # SKENARIO 2: TRUK KEMBALI / TIKET DI-LOAD (Boleh isi Timbang 2)
            if not self.edTimbang2.text():
                self.edTimbang2.setText(f"{weight:.1f}")
                self.timbang2 = weight
                self.calc_netto()
            else:
                QtWidgets.QMessageBox.information(self, "Info",
                                                  "Kedua timbang sudah terisi. Tekan Reset untuk mengulang.")

        self.perbarui_status_tombol_simpan()

    def set_new_ticket_number(self):
        """Membuat tiket baru dan mengisi field edNoTiket"""
        try:
            # Langsung panggil fungsi dari db.py dengan mengirimkan modeTransaksi
            no_tiket_baru = generate_next_no_tiket(self.modeTransaksi)
            self.edNoTiket.setText(no_tiket_baru)
        except Exception as e:
            print(f"Gagal membuat nomor tiket: {e}")
            QtWidgets.QMessageBox.warning(self, "Error DB", "Gagal generate nomor tiket otomatis.")


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
        self.is_tiket_loaded = False
        self.is_tiket_selesai = False
        self.btnTimbang.setEnabled(True)
        self.set_new_ticket_number()

    def calc_netto(self):
        self.netto = abs(self.timbang1 - self.timbang2)
        self.edNetto.setText(f"{self.netto:.1f}")

    def simpan_transaksi(self):
        try:
            no_tiket = self.edNoTiket.text().strip()

            # 1. Cegah eksekusi jika nomor tiket kosong
            if not no_tiket:
                QtWidgets.QMessageBox.warning(self, "Validasi", "Nomor tiket tidak boleh kosong.")
                return

            # 2. Validasi standar
            error = validasi_transaksi(no_tiket, self.timbang1, self.timbang2)
            if error:
                QtWidgets.QMessageBox.warning(self, "Validasi", error)
                return

            # 3. Kumpulkan data dari form UI
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

            # --- SKENARIO 1: TIKET SUDAH ADA (MODE EDIT / TIMBANG 2) ---
            if self.is_tiket_loaded:

                # Cabang 1A: HANYA EDIT TEKS
                if self.is_tiket_selesai or self.timbang2 == 0:
                    from modules.helper.transaction_handler import proses_edit_data
                    success = proses_edit_data(self.modeTransaksi, no_tiket, form_data)

                    if success:
                        QtWidgets.QMessageBox.information(self, "Berhasil", "Perubahan data teks berhasil disimpan.")
                        self.model_transaksi.reload()
                        self.reset_timbangan()
                    else:
                        QtWidgets.QMessageBox.warning(self, "Validasi", "Pemasok atau Barang tidak ditemukan.")
                    return

                # Cabang 1B: PROSES TIMBANG KELUAR
                else:
                    updated = proses_timbang_keluar(
                        self.modeTransaksi,
                        no_tiket,
                        form_data,
                        self.current_user,
                        form_data['keterangan'],
                        self.timbang2
                    )
                    if updated:
                        QtWidgets.QMessageBox.information(self, "Berhasil", "Timbang kedua berhasil disimpan.")
                        self.model_transaksi.reload()
                        self.reset_timbangan()
                    else:
                        QtWidgets.QMessageBox.warning(self, "Gagal",
                                                      "Transaksi ini sudah selesai atau tidak ditemukan.")
                    return

            # --- SKENARIO 2: TIKET BARU (TIMBANG MASUK) ---
            inserted = proses_timbang_masuk(self.modeTransaksi, no_tiket, form_data, self.current_user)
            if inserted:
                QtWidgets.QMessageBox.information(self, "Berhasil", "Timbang masuk berhasil disimpan.")
                self.model_transaksi.reload()
                self.reset_timbangan()
            else:
                QtWidgets.QMessageBox.warning(self, "Validasi", "Pemasok atau Barang tidak ditemukan.")

        except Exception as e:
            import traceback
            # Tangkap errornya dan tampilkan di layar agar aplikasi tidak force close
            pesan_error = f"Terjadi kesalahan sistem:\n{str(e)}\n\nCek terminal/console untuk detailnya."
            print(traceback.format_exc())
            QtWidgets.QMessageBox.critical(self, "Error Simpan", pesan_error)

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
            id_pemasok_pelanggan,
            timbang1, timbang2
        ) = data

        self.edNoTiket.setText(no_tiket)
        self.edNomorPolisi.setText(no_polisi)
        self.edNomorPO.setText(no_po_do)
        self.edNamaBarang.setText(get_nama_barang_by_id(id_barang) or "")
        self.edNamaSopir.setText(nama_sopir)
        self.txtedKeterangan.setPlainText(keterangan or "")
        self.nama_pemasok_pelanggan = get_nama_pemasok_pelanggan_id(self.modeTransaksi, id_pemasok_pelanggan)
        self.edPemasok.setText(self.nama_pemasok_pelanggan or "")
        self.timbang1 = timbang1
        self.timbang2 = timbang2
        self.edTimbang1.setText(f"{timbang1:.1f}" if timbang1 else "")
        self.edTimbang2.setText(f"{timbang2:.1f}" if timbang2 else "")
        self.calc_netto()

        self.is_tiket_loaded = True

        # --- LOGIKA PENGAMANAN LOADCELL ---
        if timbang2 > 0:
            self.is_tiket_selesai = True
            self.btnTimbang.setEnabled(False)  # MATIKAN TOMBOL TIMBANG
            QtWidgets.QMessageBox.information(
                self, "Mode Edit",
                "Tiket ini sudah Selesai.\nAnda hanya dapat memperbaiki data teks (Nopol, Sopir, dll). Data berat dari jembatan timbang telah dikunci."
            )
        else:
            self.is_tiket_selesai = False
            self.btnTimbang.setEnabled(True)

        # Pastikan tombol simpan aktif agar operator bisa menyimpan editan
        self.btnSave.setEnabled(True)

    def refresh_completer_edt(self, data):
        completer_value = QCompleter(data)
        completer_value.setCaseSensitivity(False)
        return completer_value

    def try_load_transaksi_tiket(self):
        no_tiket = self.edNoTiket.text().strip()
        if no_tiket:
            self.load_transaksi_untuk_timbang_kedua(no_tiket)

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

    # --- 1. Buat Helper Method agar rapi (Bebas dari Lambda Panjang) ---
    def _fetch_truk_aktif(self, offset, limit, search, sort_col, sort_order):
        return fetch_transaksi(self.modeTransaksi, offset, limit, search, sort_col, sort_order, status_timbang=0)

    def _count_truk_aktif(self, search):
        return count_transaksi(self.modeTransaksi, search, status_timbang=0)

    # --- 2. Inisialisasi Model (Cukup panggil fungsi helper) ---
    def load_data_transaksi(self):
        self.model_transaksi = ReportTableModel(
            headers=[
                "No Tiket", "No Polisi", "No PO/DO", self.modeTransaksi.capitalize(), "Barang", "Nama Sopir",
                "Gross", "Tare", "Netto", "Jam Masuk", "Jam Keluar", "Keterangan"
            ],
            fetch_callback=self._fetch_truk_aktif,
            count_callback=self._count_truk_aktif
        )

        self.tableView.setModel(self.model_transaksi)
        self.tableView.setSortingEnabled(True)
        self.model_transaksi.reload()

    # --- 3. Fungsi Toggle menjadi jauh lebih bersih ---
    def on_toggle_transaksi(self, checked):
        self.modeTransaksi = "pelanggan" if checked else "pemasok"

        self.lbl_pemasok_pelanggan.setText(self.modeTransaksi.capitalize())
        self.set_tipe_transaksi(self.modeTransaksi)

        self.edPemasok.setCompleter(self.refresh_completer_edt(get_nama_pemasok_pelanggan_aktif(self.modeTransaksi)))
        self.edNoTiket.setCompleter(self.refresh_completer_edt(get_daftar_no_tiket(self.modeTransaksi)))

        # Model akan otomatis memanggil _fetch_truk_aktif yang akan membaca self.modeTransaksi terbaru.
        if hasattr(self, 'model_transaksi'):
            self.model_transaksi.headers[3] = self.modeTransaksi.capitalize()
            self.model_transaksi.layoutChanged.emit()
            self.model_transaksi.set_search_term("")
            self.model_transaksi.reload()

        # PANGGIL FUNGSI INI UNTUK UPDATE NOMOR TIKET
        self.set_new_ticket_number()

    def _jadwalkan_pencarian(self, teks):
        self.search_term = teks
        self.search_timer.start()  # reset timer setiap ngetik


    def _lakukan_pencarian(self):
        if hasattr(self, 'model_transaksi'):
            self.model_transaksi.set_search_term(self.search_term)

    def handle_hapus(self):
        try:
            # Ambil no tiket langsung dari form (karena datanya sudah di-load)
            no_tiket = self.edNoTiket.text().strip()

            # Cegah hapus jika form kosong atau tiket belum berstatus di-load dari DB
            if not no_tiket or not self.is_tiket_loaded:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Pilih Data",
                    "Silakan load/pilih data tiket terlebih dahulu (via double-click tabel atau ketik No Tiket lalu Enter) sebelum menghapus!"
                )
                return

            # Dialog konfirmasi
            reply = QtWidgets.QMessageBox.question(
                self, 'Konfirmasi Hapus',
                f"Yakin ingin menghapus transaksi dengan tiket: {no_tiket}?\nData yang dihapus tidak bisa dikembalikan.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:

                hapus_transaksi_by_tiket(self.modeTransaksi, no_tiket)

                QtWidgets.QMessageBox.information(self, "Berhasil", "Data transaksi berhasil dihapus.")

                self.model_transaksi.reload()  # Refresh tabel
                self.reset_timbangan()  # Kosongkan form untuk tiket berikutnya

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QtWidgets.QMessageBox.critical(self, "Error Hapus", f"Terjadi kesalahan saat menghapus data:\n{str(e)}")

    def handle_tabel_dipilih(self, index):
        """Berjalan otomatis saat baris tabel di-double-click atau ditekan Enter"""
        try:
            if not index.isValid():
                return

            # Ambil nomor baris dari index yang aktif
            row = index.row()

            # Ambil nilai No Tiket di kolom ke-0 pada baris tersebut
            index_tiket = self.model_transaksi.index(row, 0)
            no_tiket = self.model_transaksi.data(index_tiket)

            if no_tiket:
                # Langsung load ke form!
                self.load_transaksi_untuk_timbang_kedua(str(no_tiket).strip())

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Gagal memuat data:\n{str(e)}")