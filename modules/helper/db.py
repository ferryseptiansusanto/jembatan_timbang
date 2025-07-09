# modules/db.py

import sqlite3
from modules.config.config import DB_PATH  # atau atur path langsung di sini
from modules.helper.konversidatetime import format_ts
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer

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
#     INSERT INTO db_master_barang (namabarang, kategori, active)
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
# rows = execute_select("SELECT id, username FROM db_master_user WHERE active = 1")
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
        WHERE active = 1 
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
        WHERE active = 1 
        ORDER BY nama
    """)
    return [r[0] for r in rows]

def get_nama_pemasok_pelanggan_id(mode_transaksi, id_pemasok_pelanggan):
    tb = "db_master_pemasok" if mode_transaksi == "pemasok" else "db_master_pelanggan"

    query = f"SELECT nama FROM {tb} WHERE active = 1 AND id = ? ORDER BY nama"
    rows = execute_select(query, (id_pemasok_pelanggan,))

    return rows[0][0] if rows else None

def get_id_pemasok_pelanggan_by_nama(mode_transaksi, nama):
    tb = "db_master_pemasok" if mode_transaksi == "pemasok" else "db_master_pelanggan"
    result = execute_select(
        f"SELECT id FROM {tb} WHERE nama = ? AND active = 1",
        (nama,)
    )
    return result[0][0] if result else None

def get_id_barang_by_nama(nama):
    result = execute_select(
        "SELECT id FROM db_master_barang WHERE namabarang = ? AND active = 1",
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

def fetch_transaksi(mode_transaksi, offset, limit, search, sort_col, sort_order, date_start=None, date_end=None):
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
        join = "LEFT JOIN db_master_pemasok s ON t.id_pemasok = s.id"
    else:
        tb = "db_transaksi_pelanggan"
        join = "LEFT JOIN db_master_pelanggan s ON t.id_pelanggan = s.id"

    sort_map = {
        0: "t.no_tiket", 1: "t.no_polisi", 2: "t.no_po_do", 3: "s.nama",
        4: "b.namabarang", 5: "t.nama_sopir", 6: "t.gross",
        7: "t.tare", 8: "t.netto", 9: "t.tanggal_masuk"
    }

    sort_field = sort_map.get(sort_col, "t.tanggal_masuk")
    direction = "ASC" if sort_order == Qt.AscendingOrder else "DESC"

    where = "WHERE t.is_timbang = 1"
    where += " AND t.tanggal_masuk >= ? AND t.tanggal_masuk < ?"

    params = []
    params += [date_start, date_end]

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
        params += [wild] * 5

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
    params += [limit, offset]
    rows = execute_select(query, params)

    for idx, r in enumerate(rows[:5]):
        print(f"[DEBUG] row {idx} length = {len(r)} | row = {r}")

    # ✨ Convert to list of tuples matching self.headers
    return rows

def count_transaksi(mode_transaksi, search="", date_start=None, date_end=None):
    if mode_transaksi == "pemasok":
        tb = "db_transaksi_pemasok"
        supplier = "db_master_pemasok"
        key = "id_pemasok"
    else:
        tb = "db_transaksi_pelanggan"
        supplier = "db_master_pelanggan"
        key = "id_pelanggan"

    where = "WHERE is_timbang = 1"
    where += " AND tanggal_masuk >= ? AND tanggal_masuk < ?"


    params = []
    params += [date_start, date_end]

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
        params += [wild] * 5

    query = f"SELECT COUNT(*) FROM {tb} {where}"
    return execute_scalar(query, params)

