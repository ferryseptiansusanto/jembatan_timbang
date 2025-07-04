# modules/print_transaksi/layout_templates.py
from modules.helper.konversidatetime import format_ts

def get_sections(data_dict):
    return [
        ("TIKET #", data_dict.get("No Tiket", "")),
        ("NOPOL", data_dict.get("No Polisi", "")),
        ("SUPPLIER", data_dict.get("Supplier", "")),
        ("BARANG", data_dict.get("Barang", "")),
        ("GROSS", f"{data_dict.get('Gross', '')} kg"),
        ("TARE", f"{data_dict.get('Tare', '')} kg"),
        ("NETTO", f"{data_dict.get('Netto', '')} kg"),
        ("TGL MASUK", format_ts(data_dict.get("Tanggal Masuk", 0))),
        ("TGL KELUAR", format_ts(data_dict.get("Tanggal Keluar", 0))),
        ("KETERANGAN", data_dict.get("Keterangan", "")),
        #("OPERATOR", current_user)
    ]