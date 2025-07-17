from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1280, 768)
        frame_geo = self.frameGeometry()
        center_point = QtWidgets.QDesktopWidget().availableGeometry().center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

        self.setup_connections()
        self.current_user = auth.get_username()
        self.current_user_level = auth.get_level()

        self.lblUser = QtWidgets.QLabel(f"User: {self.current_user}")
        self.lblLevel = QtWidgets.QLabel(f"Level: {self.current_user_level}")
        self.lblDatetime = QtWidgets.QLabel("Tanggal dan waktu...")
        self.lblComStatus = QtWidgets.QLabel("Port: -")

        self.ui.statusbar.addWidget(self.lblUser)
        self.ui.statusbar.addWidget(self.lblLevel)
        self.ui.statusbar.addPermanentWidget(self.lblDatetime)
        self.ui.statusbar.addPermanentWidget(self.lblComStatus)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # update per detik

        self.page_user = UserMain(self.current_user, self.current_user_level)
        self.page_ganti_password = GantiPasswordMain()
        self.page_barang = BarangMain(self.current_user, self.current_user_level)
        self.page_pelanggan = PelangganMain(self.current_user, self.current_user_level)
        self.page_pemasok = PemasokMain(self.current_user, self.current_user_level)
        self.page_properties = PropertiesMain(self.current_user, self.current_user_level)
        self.page_timbang = TimbangMain(self.current_user, self.current_user_level)
        self.page_print = PrintMain(self.current_user, self.current_user_level)
        self.page_editor_xml_layout = PrintMain(self.current_user, self.current_user_level)
        self.page_report_pelanggan = ReportMain(self.current_user, self.current_user_level, mode_transaksi="pelanggan")
        self.page_report_pemasok = ReportMain(self.current_user, self.current_user_level, mode_transaksi="pemasok")

        self.ui.stackedContent.addWidget(self.page_user)
        self.ui.stackedContent.addWidget(self.page_ganti_password)
        self.ui.stackedContent.addWidget(self.page_barang)
        self.ui.stackedContent.addWidget(self.page_pelanggan)
        self.ui.stackedContent.addWidget(self.page_pemasok)
        self.ui.stackedContent.addWidget(self.page_properties)
        self.ui.stackedContent.addWidget(self.page_timbang)
        self.ui.stackedContent.addWidget(self.page_print)
        self.ui.stackedContent.addWidget(self.page_editor_xml_layout)
        self.ui.stackedContent.addWidget(self.page_report_pelanggan)
        self.ui.stackedContent.addWidget(self.page_report_pemasok)

        self.lblComStatus.setStyleSheet("""
            background-color: #ffe0e0;
            color: red;
            padding: 2px 5px;
            border: 1px solid #ffaaaa;
        """)
        self.page_timbang.com_status_changed.connect(self.update_com_status)

    def update_com_status(self, port_name=None, connected=False):
        if connected and port_name:
            self.lblComStatus.setText(f"COM: {port_name} (Terhubung)")
            self.lblComStatus.setStyleSheet("color: green;")
        else:
            self.lblComStatus.setText("COM: Tidak Terhubung")
            self.lblComStatus.setStyleSheet("color: red;")

    def update_datetime(self):
        now = QtCore.QDateTime.currentDateTime()
        self.lblDatetime.setText(now.toString("dd MMM yyyy HH:mm:ss"))

    def open_user_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_user)
        self.setWindowTitle("User Management")

    def open_ganti_password_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_ganti_password)
        self.setWindowTitle("Ganti Password")

    def open_barang_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_barang)
        self.setWindowTitle("Master Barang")

    def open_pelanggan_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_pelanggan)
        self.setWindowTitle("Master Pelanggan")

    def open_pemasok_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_pemasok)
        self.setWindowTitle("Master Pemasok")

    def open_properties_form(self, taborder):
        self.page_properties.tabWidget.setCurrentIndex(taborder)
        self.ui.stackedContent.setCurrentWidget(self.page_properties)
        self.setWindowTitle("Data Perusahaan")

    def open_timbang_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_timbang)
        self.setWindowTitle("Transaksi Timbang")

    def open_print_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_print)
        self.setWindowTitle("Cetak Transaksi")

    def open_report_pelanggan_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_report_pelanggan)
        self.setWindowTitle("Laporan Transaksi Pelanggan")

    def open_report_pemasok_form(self):
        self.ui.stackedContent.setCurrentWidget(self.page_report_pemasok)
        self.setWindowTitle("Laporan Transaksi Pemasok")

    def open_editor_xml_form(self):
        # Cek apakah editor sudah ada agar tidak tambah widget berulang
        if not hasattr(self, 'page_editor_xml'):
            self.page_editor_xml = editor_template_slip.TemplateSlipEditor(self.current_user, self.current_user_level)
            self.ui.stackedContent.addWidget(self.page_editor_xml)

        self.ui.stackedContent.setCurrentWidget(self.page_editor_xml)
        self.setWindowTitle("Print Layout Editor")

    def backup_data(self):
        print(f"Proses Backup")
        folder = QFileDialog.getExistingDirectory(self, "Pilih folder backup")
        if not folder: return

        try:
            zip_path = backup_sqlite_to_zip("database/database.db", folder)
            QMessageBox.information(self, "Backup Selesai", f"📦 File disimpan:\n{zip_path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Gagal", str(e))

    def restore_data(self):
        print(f"Proses Restore")

        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih file backup", "", "Zip File (*.zip)")
        if not file_path: return

        try:
            restore_sqlite_from_zip(file_path, "database/database.db")
            QMessageBox.information(self, "Restore Selesai", "✅ Database berhasil dipulihkan.")
        except Exception as e:
            QMessageBox.critical(self, "Restore Gagal", str(e))

    def setup_connections(self):
        self.ui.actionUser_Setting.triggered.connect(self.open_user_form)
        self.ui.actionGanti_Password.triggered.connect(self.open_ganti_password_form)

        self.ui.actionMaster_Barang.triggered.connect(self.open_barang_form)
        self.ui.actionMaster_Customer.triggered.connect(self.open_pelanggan_form)
        self.ui.actionMaster_Supplier.triggered.connect(self.open_pemasok_form)
        self.ui.actionData_Perusahaan.triggered.connect(lambda: self.open_properties_form(0))
        self.ui.actionPort_Setting.triggered.connect(lambda: self.open_properties_form(1))
        self.ui.actionTimbang_Barang_2.triggered.connect(self.open_timbang_form)
        self.ui.actionPrint_Ulang_Tiket.triggered.connect(self.open_print_form)
        self.ui.actionPrint_Layout.triggered.connect(self.open_editor_xml_form)
        self.ui.actionLaporan_Supplier.triggered.connect(self.open_report_pemasok_form)
        self.ui.actionLaporan_Customer.triggered.connect(self.open_report_pelanggan_form)
        self.ui.actionBackup_Data.triggered.connect(self.backup_data)
        self.ui.actionRestore_Data.triggered.connect(self.restore_data)

        self.ui.actionExit.triggered.connect(self.close)




