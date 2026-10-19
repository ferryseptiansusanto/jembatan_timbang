# modules/db.py

import sqlite3
from modules.config.config import DB_PATH  # atau atur path langsung di sini
from modules.helper.konversidatetime import format_ts
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer
from datetime import datetime


def open_db_connection():
    return sqlite3.connect(DB_PATH)

# HOW TO USE
# from modules.db import execute_query
#
# execute_query(
#     "INSERT INTO db_master_user (username, password) VALUES (?, ?)",
#     (username, hashed)
# )
def execute_query(query, params=()):
    conn = open_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# HOW TO USE
# from modules.db import execute_many
#
# data_barang = [
#     ("Kabel NYA 2.5mm", "Listrik", 1),
#     ("Pipa PVC 3 Inch", "Plumbing", 1),
#     ("Baut 12mm", "Bahan Bangunan", 0)
# ]
#
# query = """
#     INSERT INTO db_master_barang (namabarang, kategori, status)
#     VALUES (?, ?, ?)
# """
#
# execute_many(query, data_barang)
def execute_many(query, param_list):
    conn = open_db_connection()
    cursor = conn.cursor()
    cursor.executemany(query, param_list)
    conn.commit()
    conn.close()

# HOW TO USE
# rows = execute_select("SELECT id, username FROM db_master_user WHERE status = 1")
# for row in rows:
#     print(row[0], row[1])
def execute_select(query, params=()):
    conn = open_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# HOW TO USE
# total_user = execute_scalar("SELECT COUNT(*) FROM db_master_user")
def execute_scalar(query, params=()):
    conn = open_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def init_qt_connection():
    if not QSqlDatabase.contains("qt_sql_default_connection"):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(DB_PATH)
        if not db.open():
            raise Exception(f"Gagal buka database (Qt): {db.lastError().text()}")
    return QSqlDatabase.database()

def get_nama_barang_aktif():
    rows = execute_select("""
        SELECT namabarang FROM db_master_barang 
        WHERE status = 1 
        ORDER BY namabarang
    """)
    return [r[0] for r in rows]

def get_nama_barang_by_id(id_barang):
    row = execute_select("SELECT namabarang FROM db_master_barang WHERE id = ?", (id_barang,))
    return row[0][0] if row else ""

def get_nama_pemasok_pelanggan_aktif(mode_transaksi):
    tb = "db_master_pemasok" if mode_transaksi == "pemasok" else "db_master_pelanggan"
    rows = execute_select(f"""
        SELECT nama FROM {tb} 
        WHERE status = 1 
        ORDER BY nama
    """)
    return [r[0] for r in rows]

def get_nama_pemasok_pelanggan_id(mode_transaksi, id_pemasok_pelanggan):
    tb = "db_master_pemasok" if mode_transaksi == "pemasok" else "db_master_pelanggan"

    query = f"SELECT nama FROM {tb} WHERE status = 1 AND id = ? ORDER BY nama"
    rows = execute_select(query, (id_pemasok_pelanggan,))

    return rows[0][0] if rows else None

def get_id_pemasok_pelanggan_by_nama(mode_transaksi, nama):
    tb = "db_master_pemasok" if mode_transaksi == "pemasok" else "db_master_pelanggan"
    result = execute_select(
        f"SELECT id FROM {tb} WHERE nama = ? AND status = 1",
        (nama,)
    )
    return result[0][0] if result else None

def get_id_barang_by_nama(nama):
    result = execute_select(
        "SELECT id FROM db_master_barang WHERE namabarang = ? AND status = 1",
        (nama,)
    )
    return result[0][0] if result else None

def insert_transaksi_pemasok_pelanggan(mode_transaksi, data):
    if mode_transaksi == "pemasok":
        table_name = "db_transaksi_pemasok"
        id_field = "id_pemasok"
    else:
        table_name = "db_transaksi_pelanggan"
        id_field = "id_pelanggan"

    query = f"""
        INSERT INTO {table_name} (
            no_tiket, no_polisi, no_po_do,
            {id_field}, id_barang, nama_sopir,
            gross, tare, netto,
            tanggal_masuk, keterangan,
            operator_timbang_masuk, is_timbang, timbang1, timbang2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
    """

    params = (
        data["no_tiket"],
        data["no_polisi"],
        data["no_po_do"],
        data[id_field],
        data["id_barang"],
        data["nama_sopir"],
        data["gross"],
        data["tare"],
        data["netto"],
        data["tanggal_masuk"],
        data["keterangan"],
        data["operator_timbang_masuk"],
        data["is_timbang"],
        data["timbang1"],
        data["timbang2"],
    )

    execute_query(query, params)

def is_no_tiket_exist(mode_transaksi, no_tiket):
    tb = "db_transaksi_pemasok" if mode_transaksi == "pemasok" else "db_transaksi_pelanggan"
    result = execute_scalar(
        f"SELECT COUNT(*) FROM {tb} WHERE no_tiket = ?",
        (no_tiket,)
    )
    return result > 0

def get_transaksi_by_no_tiket(mode_transaksi, no_tiket):
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
        id_pemasok_pelanggan = "id_pemasok"
    else:
        tb = "db_transaksi_pelanggan"
        id_pemasok_pelanggan = "id_pelanggan"

    query = f"""
        SELECT 
            no_tiket, no_polisi, no_po_do, 
            id_barang, nama_sopir, 
            gross, tare, netto,
            tanggal_masuk, keterangan,
            {id_pemasok_pelanggan},
            timbang1, timbang2
        FROM {tb}
        WHERE no_tiket = ?
    """
    rows = execute_select(query, (no_tiket,))
    return rows[0] if rows else None

def get_daftar_no_tiket(mode_transaksi):
    tb = "db_transaksi_pemasok" if mode_transaksi == "pemasok" else "db_transaksi_pelanggan"

    rows = execute_select(
        f"SELECT no_tiket FROM {tb} WHERE is_timbang = 0 ORDER BY tanggal_masuk DESC"
    )
    return [r[0] for r in rows]

def update_transaksi_timbang_kedua(mode_transaksi, no_tiket, data):
    tb = "db_transaksi_pemasok" if mode_transaksi == "pemasok" else "db_transaksi_pelanggan"

    fields = ", ".join([f"{k} = ?" for k in data.keys()])
    values = list(data.values())
    values.append(no_tiket)

    query = f"UPDATE {tb} SET {fields} WHERE no_tiket = ?"
    execute_query(query, values)


def fetch_transaksi(mode_transaksi, offset, limit, search, sort_col, sort_order, date_start=None, date_end=None, status_timbang=None):
    # 1. Penentuan Tabel dan Relasi (JOIN)
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
        join = "LEFT JOIN db_master_pemasok s ON t.id_pemasok = s.id"
    else:
        tb = "db_transaksi_pelanggan"
        join = "LEFT JOIN db_master_pelanggan s ON t.id_pelanggan = s.id"

    # 2. Pemetaan Kolom untuk Sorting
    sort_map = {
        0: "t.no_tiket", 1: "t.no_polisi", 2: "t.no_po_do", 3: "s.nama",
        4: "b.namabarang", 5: "t.nama_sopir", 6: "t.gross",
        7: "t.tare", 8: "t.netto", 9: "t.tanggal_masuk"
    }
    sort_field = sort_map.get(sort_col, "t.tanggal_masuk")

    # Menangani arah sort agar aman dari bentrok Enum PyQt dan String biasa
    if isinstance(sort_order, str):
        direction = sort_order
    else:
        direction = "ASC" if sort_order == Qt.AscendingOrder else "DESC"

    # 3. Logika Filter Pintar (Penengah UI)
    where = "WHERE 1=1"
    params = []

    if date_start is not None and date_end is not None:
        # Jika dipanggil dari REPORT MAIN (Ada Tanggal) -> Tampilkan Histori Truk Selesai
        where += " AND t.tanggal_masuk >= ? AND t.tanggal_masuk < ?"
        params.extend([date_start, date_end])

    if status_timbang is not None:
        where += " AND t.is_timbang = ?"
        params.append(status_timbang)

    # 4. Filter Pencarian Teks
    if search:
        where += """
        AND (
            t.no_tiket LIKE ? OR
            t.no_polisi LIKE ? OR
            t.nama_sopir LIKE ? OR
            b.namabarang LIKE ? OR
            s.nama LIKE ?
        )
        """
        wild = f"%{search}%"
        params.extend([wild] * 5)

    # 5. Perakitan dan Eksekusi SQL
    query = f"""
        SELECT 
            t.no_tiket, t.no_polisi, t.no_po_do,
            s.nama AS Supplier,
            b.namabarang AS Barang,
            t.nama_sopir,
            t.gross, t.tare, t.netto,
            t.tanggal_masuk, t.tanggal_keluar,
            t.keterangan
        FROM {tb} t
        LEFT JOIN db_master_barang b ON t.id_barang = b.id
        {join}
        {where}
        ORDER BY {sort_field} {direction}
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    return execute_select(query, params)


def count_transaksi(mode_transaksi, search="", date_start=None, date_end=None, status_timbang=1):
    # 1. Penentuan Tabel
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
        supplier = "db_master_pemasok"
        key = "id_pemasok"
    else:
        tb = "db_transaksi_pelanggan"
        supplier = "db_master_pelanggan"
        key = "id_pelanggan"

    # 2. Logika Filter Pintar (Penengah UI)
    where = "WHERE 1=1"
    params = []

    if date_start is not None and date_end is not None:
        # Jika dari REPORT MAIN
        where += " AND tanggal_masuk >= ? AND tanggal_masuk < ?"
        params.extend([date_start, date_end])

    # Filter Status Timbang (dinamis berdasarkan argumen)
    if status_timbang is not None:
        where += " AND is_timbang = ?"
        params.append(status_timbang)

    # 3. Filter Pencarian Teks (Sub-query untuk tabel relasi)
    if search:
        where += f"""
        AND (
            no_tiket LIKE ? OR
            no_polisi LIKE ? OR
            nama_sopir LIKE ? OR
            id_barang IN (
                SELECT id FROM db_master_barang WHERE namabarang LIKE ?
            ) OR
            {key} IN (
                SELECT id FROM {supplier} WHERE nama LIKE ?
            )
        )
        """
        wild = f"%{search}%"
        params.extend([wild] * 5)

    # 4. Eksekusi SQL Hitung Total
    query = f"SELECT COUNT(*) FROM {tb} {where}"
    return execute_scalar(query, params)


def generate_next_no_tiket(mode_transaksi):
    """
    Generate nomor tiket 8 digit: YYMMNNNN menggunakan MAX()
    Contoh: 26100001 (Tahun 26, Bulan 10, Urutan 0001)
    """
    if mode_transaksi == "pelanggan":
        table_name = "db_transaksi_pelanggan"
    else:
        table_name = "db_transaksi_pemasok"

    now = datetime.now()
    prefix = now.strftime("%y%m")  # Contoh output: "2610" untuk Oktober 2026

    # Kita bisa memanfaatkan execute_scalar yang sudah ada di file ini
    query = f"SELECT MAX(no_tiket) FROM {table_name} WHERE no_tiket LIKE ?"

    # execute_scalar mengembalikan nilai tunggal, jika tidak ada tiket akan return None
    last_ticket = execute_scalar(query, (f"{prefix}%",))

    if last_ticket:
        last_ticket_str = str(last_ticket).strip()
        try:
            # Ambil 4 digit terakhir dan tambahkan 1
            last_seq = int(last_ticket_str[-4:])
            next_seq = last_seq + 1
        except ValueError:
            next_seq = 1
    else:
        # Jika belum ada data tiket sama sekali di bulan tersebut
        next_seq = 1

    # Format menjadi string dengan leading zero 4 digit
    return f"{prefix}{next_seq:04d}"

def get_selected_tiket(self):
    """Mendapatkan No Tiket dari baris yang diklik di tabel"""
    indexes = self.tableView.selectionModel().selectedRows()
    if not indexes:
        return None

    # Ambil baris pertama yang di-select
    row = indexes[0].row()

    # Kolom 0 adalah No Tiket (berdasarkan headers di ReportTableModel)
    index_tiket = self.model_transaksi.index(row, 0)
    no_tiket = self.model_transaksi.data(index_tiket)
    return str(no_tiket).strip()

def hapus_transaksi_by_tiket(mode_transaksi, no_tiket):
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
    else:
        tb = "db_transaksi_pelanggan"

    query = f"DELETE FROM {tb} WHERE no_tiket = ?"
    execute_query(query, (no_tiket,))