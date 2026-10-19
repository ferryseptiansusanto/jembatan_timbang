import os
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog

from modules.config.config import DB_PATH
from modules.main_window.form_main import Ui_MainWindow
from modules.master_user.ganti_password_main import GantiPasswordMain
from modules.master_user.user_main import UserMain
from modules.master_barang.barang_main import BarangMain
from modules.master_pelanggan.pelanggan_main import PelangganMain
from modules.master_pemasok.pemasok_main import PemasokMain
from modules.properties.properties_main import PropertiesMain
from modules.timbang_barang.timbang_main import  TimbangMain
from modules.print_transaksi.print_main import  PrintMain
from modules.report.report_main import ReportMain
from modules.helper import auth
from modules.xml_editor import editor_template_slip
from modules.helper.db_utils import backup_sqlite_to_zip, restore_sqlite_from_zip
import faulthandler

faulthandler.enable()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1280, 768)

        #Center Window
        frame_geo = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

        self.current_user = auth.get_username()
        self.current_user_level = auth.get_level()

        self.setup_statusbar()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # update per detik

        self.setup_pages()
        self.setup_connections()


    def setup_statusbar(self):
        """Pisahkan logika statusbar agar __init__ lebih rapi"""
        self.lblUser = QtWidgets.QLabel(f"User: {self.current_user}")
        self.lblLevel = QtWidgets.QLabel(f"Level: {self.current_user_level}")
        self.lblDatetime = QtWidgets.QLabel("Tanggal dan waktu...")
        self.lblComStatus = QtWidgets.QLabel("Port: -")

        self.ui.statusbar.addWidget(self.lblUser)
        self.ui.statusbar.addWidget(self.lblLevel)
        self.ui.statusbar.addPermanentWidget(self.lblDatetime)
        self.ui.statusbar.addPermanentWidget(self.lblComStatus)

        self.lblComStatus.setStyleSheet("""
            background-color: #ffe0e0; color: red; padding: 2px 5px; border: 1px solid #ffaaaa;
        """)

    def setup_pages(self):
        """Inisialisasi semua halaman dan masukkan ke stackedWidget dengan looping"""
        u, lvl = self.current_user, self.current_user_level

        self.page_user = UserMain(u, lvl)
        self.page_ganti_password = GantiPasswordMain()
        self.page_barang = BarangMain(u, lvl)
        self.page_pelanggan = PelangganMain(u, lvl)
        self.page_pemasok = PemasokMain(u, lvl)
        self.page_properties = PropertiesMain(u, lvl)
        self.page_timbang = TimbangMain(u, lvl)
        self.page_print = PrintMain(u, lvl)
        self.page_editor_xml_layout = PrintMain(u, lvl)
        self.page_report_pelanggan = ReportMain(u, lvl, mode_transaksi="pelanggan")
        self.page_report_pemasok = ReportMain(u, lvl, mode_transaksi="pemasok")

        # Kumpulkan dalam list, lalu loop untuk addWidget
        pages = [
            self.page_user, self.page_ganti_password, self.page_barang,
            self.page_pelanggan, self.page_pemasok, self.page_properties,
            self.page_timbang, self.page_print,
            self.page_report_pelanggan, self.page_report_pemasok
        ]


        pages = [
            self.page_user, self.page_ganti_password, self.page_barang,
            self.page_pelanggan, self.page_pemasok, self.page_properties,
            self.page_timbang, self.page_print,
            self.page_report_pelanggan, self.page_report_pemasok
        ]

        for page in pages:
            self.ui.stackedContent.addWidget(page)

        self.page_timbang.com_status_changed.connect(self.update_com_status)

    def switch_page(self, widget, title):
        """Satu fungsi universal untuk mengganti halaman dan judul"""
        self.ui.stackedContent.setCurrentWidget(widget)
        self.setWindowTitle(title)

    def open_properties_form(self, taborder):
        """Fungsi ini dipertahankan karena ada logika khusus (setCurrentIndex)"""
        self.page_properties.tabWidget.setCurrentIndex(taborder)
        self.switch_page(self.page_properties, "Data Perusahaan")

    def open_editor_xml_form(self):
        """Dipertahankan karena menggunakan lazy-loading (dibuat saat diklik)"""
        if not hasattr(self, 'page_editor_xml'):
            self.page_editor_xml = editor_template_slip.TemplateSlipEditor(self.current_user, self.current_user_level)
            self.ui.stackedContent.addWidget(self.page_editor_xml)
        self.switch_page(self.page_editor_xml, "Print Layout Editor")

    def update_com_status(self, port_name=None, connected=False):
        if connected and port_name:
            self.lblComStatus.setText(f"COM: {port_name} (Terhubung)")
            self.lblComStatus.setStyleSheet("""
                background-color: #e0ffe0; color: green; padding: 2px 5px; border: 1px solid #aaffaa;
            """)
        else:
            self.lblComStatus.setText("COM: Tidak Terhubung")
            self.lblComStatus.setStyleSheet("""
                background-color: #ffe0e0; color: red; padding: 2px 5px; border: 1px solid #ffaaaa;
            """)

    def update_datetime(self):
        now = QtCore.QDateTime.currentDateTime()
        self.lblDatetime.setText(now.toString("dd MMM yyyy HH:mm:ss"))


    def backup_data(self):
        print(f"Proses Backup")
        folder = QFileDialog.getExistingDirectory(self, "Pilih folder backup")
        if not folder: return

        try:
            zip_path = backup_sqlite_to_zip( DB_PATH, folder)
            QMessageBox.information(self, "Backup Selesai", f"📦 File disimpan:\n{zip_path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Gagal", str(e))

    def log_off(self):
        from modules.Login.login_main import LoginMain  # Import lokal untuk hindari circular import
        auth.set_user(None, None, None)
        self.login_form = LoginMain()
        self.login_form.show()
        self.close()

    def restore_data(self):
        print(f"Proses Restore")

        # 1. Pilih file backup
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih file backup", "", "Zip File (*.zip)")
        if not file_path:
            return

        # 2. Munculkan dialog konfirmasi yang tegas
        reply = QMessageBox.question(
            self,
            'Konfirmasi Restore',
            "PERINGATAN BAHAYA:\n\nProses ini akan MENGHAPUS database saat ini dan menggantinya dengan data dari file backup.\n\nSemua data transaksi terbaru yang belum di-backup akan HILANG secara permanen.\n\nApakah Anda YAKIN ingin melanjutkan?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                import os
                import gc  # Module untuk membersihkan memori/koneksi yang menggantung
                from PyQt5.QtSql import QSqlDatabase

                # --- 1. PAKSA TUTUP KONEKSI DATABASE PYQT5 (Jika Anda memakainya) ---
                for conn_name in QSqlDatabase.connectionNames():
                    db = QSqlDatabase.database(conn_name)
                    if db.isOpen():
                        db.close()
                    QSqlDatabase.removeDatabase(conn_name)

                # --- 2. BERSIHKAN VARIABEL LOKAL YANG MENGUNCI SQLITE3 ---
                # Ini akan memaksa Python mematikan koneksi database yang lupa ditutup di background
                gc.collect()

                # --- 3. HAPUS DATABASE LAMA ---
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)

                # --- 4. EKSTRAK / RESTORE DATA BARU ---
                restore_sqlite_from_zip(file_path, DB_PATH)

                QMessageBox.information(
                    self,
                    "Restore Selesai",
                    "✅ Database berhasil dipulihkan!\n\nAplikasi akan melakukan Log Off otomatis untuk memuat ulang data baru."
                )

                self.log_off()

            except PermissionError:
                QMessageBox.critical(
                    self,
                    "Restore Gagal",
                    "Database masih dikunci oleh sistem!\n\nJika error ini masih muncul, pastikan tidak ada variabel koneksi (conn) yang bersifat global di file 'db_utils' atau 'db.py' Anda yang belum di-close()."
                )
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                QMessageBox.critical(self, "Restore Gagal", f"Terjadi kesalahan sistem:\n{str(e)}")
        # ==================== FUNGSI KONEKSI ====================
    def setup_connections(self):
        # Gunakan lambda untuk memanggil switch_page dengan parameter
        self.ui.actionUser_Setting.triggered.connect(lambda: self.switch_page(self.page_user, "User Management"))
        self.ui.actionGanti_Password.triggered.connect(
            lambda: self.switch_page(self.page_ganti_password, "Ganti Password"))
        self.ui.actionMaster_Barang.triggered.connect(lambda: self.switch_page(self.page_barang, "Master Barang"))
        self.ui.actionMaster_Customer.triggered.connect(
            lambda: self.switch_page(self.page_pelanggan, "Master Pelanggan"))
        self.ui.actionMaster_Supplier.triggered.connect(
            lambda: self.switch_page(self.page_pemasok, "Master Pemasok"))
        self.ui.actionTimbang_Barang_2.triggered.connect(
            lambda: self.switch_page(self.page_timbang, "Transaksi Timbang"))
        self.ui.actionPrint_Ulang_Tiket.triggered.connect(
            lambda: self.switch_page(self.page_print, "Cetak Transaksi"))
        self.ui.actionLaporan_Supplier.triggered.connect(
            lambda: self.switch_page(self.page_report_pemasok, "Laporan Transaksi Pemasok"))
        self.ui.actionLaporan_Customer.triggered.connect(
            lambda: self.switch_page(self.page_report_pelanggan, "Laporan Transaksi Pelanggan"))

        # Menu dengan logika khusus
        self.ui.actionData_Perusahaan.triggered.connect(lambda: self.open_properties_form(0))
        self.ui.actionPort_Setting.triggered.connect(lambda: self.open_properties_form(1))
        self.ui.actionPrint_Layout.triggered.connect(self.open_editor_xml_form)

        # Menu sistem
        self.ui.actionBackup_Data.triggered.connect(self.backup_data)
        self.ui.actionRestore_Data.triggered.connect(self.restore_data)
        self.ui.actionLog_Off.triggered.connect(self.log_off)
        self.ui.actionExit.triggered.connect(self.close)
