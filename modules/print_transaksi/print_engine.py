import re

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPainter, QFont, QFontMetrics
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRectF, Qt

from modules.print_transaksi.print_utils import mmX, mmY
from modules.print_transaksi.layout_templates import get_sections
from modules.print_transaksi.signature_box import draw_signature_area_centered
from modules.helper.messagebox_utils import show_info
from modules.print_transaksi.layout_config import get_slip_layout

def cetak_slip(parent, current_user, data_dict, format_slip="A6"):
    # Ambil layout berdasarkan profil
    width_mm, height_mm, margin = get_slip_layout(format_slip)

    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageSize(QPrinter.A6)  # Tetap pakai A6 default, atau bisa pakai Custom
    printer.setOrientation(QPrinter.Portrait)
    printer.setFullPage(True)

    painter = QPainter()
    if not painter.begin(printer):
        QMessageBox.warning(parent, "Cetak", "Gagal membuka printer.")
        return

    # Font
    font_title = QFont("Helvetica", 18, QFont.Bold)
    font_label = QFont("Helvetica", 10)
    font_value = QFont("Helvetica", 10, QFont.Bold)

    # Posisi awal
    x_left = mmX(printer, margin["left"])
    x_right = mmX(printer, margin["left"] + 25)
    y_mm = margin["top"]
    line_height_mm = 7

    # Header
    for text, font in [
        (parent.nama_perusahaan, font_title),
        (parent.alamat_perusahaan, font_label),
        (parent.telepon_perusahaan, font_label)
    ]:
        painter.setFont(font)
        rect = QRectF(0, mmY(printer, y_mm), mmX(printer, width_mm), mmY(printer, 9))
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignTop, text)
        y_mm += line_height_mm + 1

    painter.drawLine(x_left, mmY(printer, y_mm), mmX(printer, width_mm - margin["right"]), mmY(printer, y_mm))
    y_mm += line_height_mm

    # Detail
    for label, value in get_sections(data_dict):
        if label == "KETERANGAN":
            y_mm = draw_keterangan_fixed(
                painter, printer, label, value,
                font_label, font_value,
                y_mm
            )
        else:
            painter.setFont(font_label)
            painter.drawText(x_left, mmY(printer, y_mm), label)
            painter.setFont(font_value)
            painter.drawText(x_right, mmY(printer, y_mm), f": {value}")
            y_mm += line_height_mm

    # Tanda tangan
    y_mm += 10
    draw_signature_area_centered(
        painter, mmY(printer, y_mm), printer,
        data_dict.get("Nama Sopir", ""), current_user
    )

    # Footer
    y_mm += 60
    painter.setFont(QFont("Helvetica", 9))
    painter.drawText(x_left, mmY(printer, y_mm), "Dicetak oleh Sistem Jembatan Timbang")

    painter.end()
    show_info(parent, "Slip berhasil dicetak ke printer.", "Cetak")

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
