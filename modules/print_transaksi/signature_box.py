# modules/print_transaksi/signature_box.py
from PyQt5.QtGui import QFont
from modules.print_transaksi.print_utils import mmX, mmY
from PyQt5.QtCore import QRectF, Qt


def draw_signature_area(painter, x, y, printer, nama_sopir, nama_operator):
    spacing = mmX(printer, 40)
    painter.setFont(QFont("Helvetica", 10, QFont.Bold))

    painter.drawText(x, y, f"Operator:")
    painter.drawText(x + spacing, y, f"Sopir:")


    y += mmY(printer, 10)

    painter.setFont(QFont("Helvetica", 10))
    painter.drawText(x, y, f"{nama_operator}")
    painter.drawText(x + spacing, y, f"{nama_sopir}")

def draw_signature_area_centered(painter, y, printer, nama_sopir, nama_operator):
    box_w = mmX(printer, 30)
    spacing = mmX(printer, 10)
    total_w = box_w * 2 + spacing

    x_center = printer.pageRect().width() // 2
    x_left = x_center - total_w // 2
    x_right = x_left + box_w + spacing

    # Label tanpa "Tanda Tangan"
    painter.setFont(QFont("Helvetica", 10, QFont.Bold))
    painter.drawText(x_left, y, "Operator")
    painter.drawText(x_right, y, "Sopir")

    y += mmY(printer, 20)

    painter.setFont(QFont("Helvetica", 10))
    painter.drawText(x_left, y, nama_operator)
    painter.drawText(x_right, y, nama_sopir)
