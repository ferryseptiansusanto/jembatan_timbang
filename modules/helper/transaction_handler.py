from time import time
from PyQt5.QtWidgets import QMessageBox
from modules.helper.db import (
    insert_transaksi_pemasok_pelanggan,
    update_transaksi_timbang_kedua,
    get_transaksi_by_no_tiket,
    get_id_barang_by_nama,
    get_id_pemasok_pelanggan_by_nama
)

def hitung_gross_tare(t1, t2):
    gross, tare = (t1, t2) if t1 > t2 else (t2, t1)
    is_timbang = 1 if t1 > 0 and t2 > 0 else 0
    return gross, tare, is_timbang

def validasi_transaksi(no_tiket, t1, t2):
    if not no_tiket:
        return "No Tiket wajib diisi."
    if t1 == t2 and t1 > 0:
        return "Berat timbang 1 dan timbang 2 tidak boleh sama."
    return None

def proses_timbang_keluar(mode, no_tiket, data_update, current_user, keterangan, timbang2):
    existing = get_transaksi_by_no_tiket(mode, no_tiket)
    if not existing or existing[-1] == 1:
        return False  # Sudah selesai atau tidak ada
    gross, tare, is_timbang = hitung_gross_tare(data_update['timbang1'], timbang2)

    updated = {
        "gross": gross,
        "tare": tare,
        "netto": abs(data_update['timbang1'] - timbang2),
        "tanggal_keluar": int(time()),
        "keterangan": keterangan,
        "operator_timbang_keluar": current_user,
        "timbang2": timbang2,
        "is_timbang": is_timbang
    }

    update_transaksi_timbang_kedua(mode, no_tiket, updated)
    return True

def proses_timbang_masuk(mode, no_tiket, form_data, current_user):
    id_pemasok_pelanggan = get_id_pemasok_pelanggan_by_nama(mode, form_data['pemasok'])
    id_barang = get_id_barang_by_nama(form_data['barang'])
    if not id_pemasok_pelanggan or not id_barang:
        return False

    gross, tare, is_timbang = hitung_gross_tare(form_data['timbang1'], form_data['timbang2'])

    id_field = "id_pemasok" if mode == "pemasok" else "id_pelanggan"
    data_insert = {
        "no_tiket": no_tiket,
        "no_polisi": form_data['nopol'],
        "no_po_do": form_data['nopo'],
        id_field: id_pemasok_pelanggan,
        "id_barang": id_barang,
        "nama_sopir": form_data['sopir'],
        "gross": gross,
        "tare": tare,
        "netto": abs(form_data['timbang1'] - form_data['timbang2']),
        "tanggal_masuk": int(time()),
        "keterangan": form_data['keterangan'],
        "operator_timbang_masuk": current_user,
        "is_timbang": is_timbang,
        "timbang1": form_data['timbang1'],
        "timbang2": form_data['timbang2']
    }

    insert_transaksi_pemasok_pelanggan(mode, data_insert)
    return True