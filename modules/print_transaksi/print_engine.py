import re

from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QPainter, QFont, QFontMetrics
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRectF, Qt
from modules.helper.konversidatetime import format_ts

from modules.helper.xmlconfigurator import bacaslipxml
from modules.print_transaksi.print_utils import mmX, mmY
from modules.print_transaksi.layout_templates import get_sections
from modules.print_transaksi.signature_box import draw_signature_area_centered
from modules.helper.messagebox_utils import show_info
from modules.print_transaksi.layout_config import get_slip_layout


def cetak_slip(parent, current_user, data_dict, format_slip="A6"):
    """Fungsi utama dengan Opsi Cetak atau Preview"""

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Opsi Cetak")
    msg_box.setText("Silakan pilih metode cetak untuk tiket ini:")
    msg_box.setIcon(QMessageBox.Question)

    btn_preview = msg_box.addButton("Preview", QMessageBox.ActionRole)
    btn_cetak = msg_box.addButton("Cetak Langsung", QMessageBox.ActionRole)
    btn_batal = msg_box.addButton("Batal", QMessageBox.RejectRole)

    msg_box.exec_()
    if msg_box.clickedButton() == btn_batal:
        return

    # Inisialisasi Printer Dasar (Gunakan A6 atau kustom sesuai CSS Anda)
    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageSize(QPrinter.A6)
    printer.setOrientation(QPrinter.Portrait)
    printer.setFullPage(True)

    if msg_box.clickedButton() == btn_preview:
        preview_dialog = QPrintPreviewDialog(printer, parent)
        preview_dialog.setWindowTitle("Preview Cetak Tiket Timbang")
        preview_dialog.resize(800, 600)
        preview_dialog.paintRequested.connect(
            lambda p: _draw_slip(p, parent, current_user, data_dict)
        )
        preview_dialog.exec_()

    elif msg_box.clickedButton() == btn_cetak:
        print_dialog = QPrintDialog(printer, parent)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            _draw_slip(printer, parent, current_user, data_dict)


def _draw_slip(printer, parent, current_user, data_dict):
    """Fungsi internal untuk menggambar layout ke printer menggunakan HTML dari XML"""

    html_template = bacaslipxml()
    if not html_template or html_template.strip() == "":
        html_template = "<h3>Error: Template Slip (XML) belum dikonfigurasi!</h3>"

    # 1. Profil Perusahaan
    html_content = html_template.replace("{{nama_perusahaan}}", str(parent.company.nama))
    html_content = html_content.replace("{{alamat}}", str(parent.company.alamat))
    html_content = html_content.replace("{{telepon}}", str(parent.company.telepon))

    # 2. Data General (Pencarian Kunci yang Kebal / Bulletproof)
    html_content = html_content.replace("{{no_tiket}}", str(data_dict.get("No Tiket", "-")))
    html_content = html_content.replace("{{no_polisi}}", str(data_dict.get("No Polisi", "-")))
    html_content = html_content.replace("{{no_do}}", str(data_dict.get("No PO/DO", "-")))

    supplier_val = data_dict.get("Supplier", data_dict.get("Nama Supplier", data_dict.get("Pelanggan", data_dict.get(
        "Nama Pelanggan", "-"))))
    barang_val = data_dict.get("Barang", data_dict.get("Nama Barang", "-"))
    html_content = html_content.replace("{{supplier}}", str(supplier_val))
    html_content = html_content.replace("{{barang}}", str(barang_val))

    # 3. Format Tanggal
    try:
        tgl_m = format_ts(data_dict.get("Tanggal Masuk", 0))
    except:
        tgl_m = str(data_dict.get("Tanggal Masuk", "-"))

    try:
        tgl_k = format_ts(data_dict.get("Tanggal Keluar", 0))
    except:
        tgl_k = str(data_dict.get("Tanggal Keluar", "-"))

    html_content = html_content.replace("{{tanggal_masuk}}", tgl_m)
    html_content = html_content.replace("{{tanggal_keluar}}", tgl_k)

    # 4. Format Angka Ribuan (Titik gaya Indonesia)
    def format_angka(val):
        try:
            # Ubah "27934" -> "27,934" -> "27.934"
            return "{:,.0f}".format(float(val)).replace(",", ".")
        except:
            return str(val)

    html_content = html_content.replace("{{gross}}", format_angka(data_dict.get("Gross", 0)))
    html_content = html_content.replace("{{tare}}", format_angka(data_dict.get("Tare", 0)))
    html_content = html_content.replace("{{netto}}", format_angka(data_dict.get("Netto", 0)))

    # 5. Footer & Keterangan
    html_content = html_content.replace("{{nama_sopir}}", str(data_dict.get("Nama Sopir", "-")))
    html_content = html_content.replace("{{user}}", str(current_user))
    html_content = html_content.replace("{{keterangan}}", str(data_dict.get("Keterangan", "-")))

    document = QTextDocument()
    document.setHtml(html_content)
    document.print_(printer)


def draw_keterangan_fixed(painter, printer, label, text, font_label, font_value, y_mm):
    x_left_mm = 10
    width_mm = 90
    height_mm = 15

    x_left = mmX(printer, x_left_mm)
    y_label = mmY(printer, y_mm)

    # Gambar label
    painter.setFont(font_label)
    painter.drawText(x_left, y_label, label)

    # Geser Y untuk isi
    y_mm += 5
    y_value = mmY(printer, y_mm)

    # Bungkus teks panjang
    painter.setFont(font_value)
    value_text = soft_wrap(text.strip() or "-", chunk_size=24)

    max_width_px = mmX(printer, width_mm)
    fixed_height_px = mmY(printer, height_mm)

    value_rect = QRectF(x_left, y_value, max_width_px, fixed_height_px)
    painter.drawText(value_rect, Qt.TextWordWrap | Qt.AlignTop, value_text)

    return y_mm + height_mm + 2
def soft_wrap(text, chunk_size=30):
    """
    Memecah teks panjang tanpa spasi menjadi potongan berbasis chunk_size.
    Cocok untuk teks dengan kata sambung seperti 'test2test2test2...'
    """
    text = text.strip()
    if not text:
        return "-"

    # Jika sudah ada spasi, biarkan apa adanya
    if " " in text:
        return text

    # Tambahkan spasi setiap N karakter
    return re.sub(f"(.{{{chunk_size}}})", r"\1 ", text)
