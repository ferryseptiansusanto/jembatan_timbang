# modules/print_transaksi/printer_utils.py

def mmX(printer, val):
    return int(val * printer.logicalDpiX() / 25.4)

def mmY(printer, val):
    return int(val * printer.logicalDpiY() / 25.4)