from modules.helper.db import execute_select, execute_scalar
from PyQt5.QtCore import Qt

class ReportHandler:
    def __init__(self, mode_transaksi="pelanggan", limit=100):
        self.mode_transaksi = mode_transaksi.lower()
        self.limit = limit

    def get_table_info(self):
        if self.mode_transaksi == "pemasok":
            return {
                "trans": "db_transaksi_pemasok",
                "master": "db_master_pemasok",
                "key": "id_pemasok"
            }
        else:
            return {
                "trans": "db_transaksi_pelanggan",
                "master": "db_master_pelanggan",
                "key": "id_pelanggan"
            }

    def fetch_report_data(self, tgl_awal, tgl_akhir, keyword=""):
        info = self.get_table_info()
        query = f"""
            SELECT 
                t.no_tiket, t.no_polisi, t.no_po_do,
                r.nama AS nama_relasi,
                b.namabarang AS barang,
                t.nama_sopir,
                t.gross, t.tare, t.netto,
                t.tanggal_masuk, t.tanggal_keluar,
                t.keterangan
            FROM {info['trans']} t
            LEFT JOIN db_master_barang b ON t.id_barang = b.id
            LEFT JOIN {info['master']} r ON t.{info['key']} = r.id
            WHERE DATE(t.tanggal_masuk) BETWEEN ? AND ?
              AND t.is_timbang = 1
        """

        params = [tgl_awal.strftime('%Y-%m-%d'), tgl_akhir.strftime('%Y-%m-%d')]

        if keyword:
            query += """
            AND (
                t.no_polisi LIKE ? OR
                t.no_tiket LIKE ? OR
                r.nama LIKE ? OR
                b.namabarang LIKE ?
            )
            """
            wild = f"%{keyword}%"
            params += [wild] * 4

        query += " ORDER BY t.tanggal_masuk DESC"

        rows = execute_select(query, params)
        return [dict(r) for r in rows]

    def lazy_fetch(self, offset, limit, search="", sort_col=None, sort_order=Qt.AscendingOrder):
        info = self.get_table_info()
        direction = "ASC" if sort_order == Qt.AscendingOrder else "DESC"
        sort_map = {
            0: "no_tiket", 1: "no_polisi", 2: "no_po_do",
            3: "nama_sopir", 4: "gross", 5: "tare",
            6: "netto", 7: "tanggal_masuk"
        }
        sort_field = sort_map.get(sort_col, "tanggal_masuk")

        where_clause = "WHERE t.is_timbang = 1"
        if search:
            where_clause += f" AND (t.no_tiket LIKE '%{search}%' OR t.no_polisi LIKE '%{search}%')"

        query = f"""
            SELECT 
                t.no_tiket, t.no_polisi, t.no_po_do,
                r.nama AS Supplier,
                b.namabarang AS Barang,
                t.nama_sopir, t.gross, t.tare, t.netto,
                t.tanggal_masuk, t.tanggal_keluar,
                t.keterangan
            FROM {info['trans']} t
            LEFT JOIN db_master_barang b ON t.id_barang = b.id
            LEFT JOIN {info['master']} r ON t.{info['key']} = r.id
            {where_clause}
            ORDER BY {sort_field} {direction}
            LIMIT ? OFFSET ?
        """
        return execute_select(query, [limit, offset])

    def count_lazy(self, search=""):
        info = self.get_table_info()
        query = f"SELECT COUNT(*) FROM {info['trans']} WHERE is_timbang = 1"
        if search:
            query += f" AND (no_tiket LIKE '%{search}%' OR no_polisi LIKE '%{search}%')"
        return execute_scalar(query)