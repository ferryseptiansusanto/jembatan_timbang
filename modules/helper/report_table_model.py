from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from modules.helper.konversidatetime import format_ts


class ReportTableModel(QAbstractTableModel):
    def __init__(self, headers, fetch_callback, count_callback=None, batch_size=100, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.batch_size = batch_size
        self.fetch_callback = fetch_callback
        self.count_callback = count_callback

        self.search_term = ""
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder

        self.data_rows = []
        self.end_of_data = False

        # PENGAMAN STACK OVERFLOW (Re-entrancy Guard)
        self._is_fetching = False

    def set_search_term(self, term):
        term = term.strip()
        if term != self.search_term:
            self.search_term = term
            self.reload()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.data_rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row, col = index.row(), index.column()
            try:
                value = self.data_rows[row][col]
                if value is None or str(value).strip() == "":
                    return ""

                # Format Tanggal Masuk & Keluar
                if col in [9, 10]:
                    try:
                        return format_ts(value)
                    except Exception:
                        return str(value)

                # Format Angka
                if col in [6, 7, 8]:
                    try:
                        return "{:,.2f}".format(float(value))
                    except Exception:
                        return str(value)

                return str(value)
            except Exception as e:
                print(f"[ERROR UI] Gagal render baris {row}, col {col}: {e}")
                return ""

        elif role == Qt.TextAlignmentRole:
            if index.column() in [6, 7, 8]:
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        return None

    def sort(self, column, order=Qt.AscendingOrder):
        # PENCEGAHAN INFINITE LOOP DARI VIEW
        if self.sort_column == column and self.sort_order == order and len(self.data_rows) > 0:
            return

        self.layoutAboutToBeChanged.emit()
        self.sort_column = column
        self.sort_order = order
        self.data_rows.clear()
        self.end_of_data = False
        self._fetch_internal()
        self.layoutChanged.emit()

    def reload(self):
        # Mencegah reload bertumpuk
        if self._is_fetching: return

        self.beginResetModel()
        self.data_rows.clear()
        self.end_of_data = False
        self._fetch_internal()
        self.endResetModel()

    def _fetch_internal(self):
        if not self.fetch_callback or self._is_fetching: return

        self._is_fetching = True  # KUNCI GEMBOK
        order_sql = "ASC" if self.sort_order == Qt.AscendingOrder else "DESC"

        try:
            rows = self.fetch_callback(0, self.batch_size, self.search_term, self.sort_column, order_sql)
            if rows:
                self.data_rows.extend(list(rows))
            else:
                self.end_of_data = True
        except Exception as e:
            print(f"[ERROR DB] Gagal menarik data: {e}")
        finally:
            self._is_fetching = False  # BUKA GEMBOK

    def fetchMore(self, parent=QModelIndex()):
        if not self.fetch_callback or self.end_of_data or self._is_fetching:
            return

        self._is_fetching = True  # KUNCI GEMBOK
        offset = len(self.data_rows)
        order_sql = "ASC" if self.sort_order == Qt.AscendingOrder else "DESC"

        try:
            rows = self.fetch_callback(offset, self.batch_size, self.search_term, self.sort_column, order_sql)
            if rows:
                self.beginInsertRows(QModelIndex(), offset, offset + len(rows) - 1)
                self.data_rows.extend(list(rows))
                self.endInsertRows()
            else:
                self.end_of_data = True
        except Exception as e:
            print(f"[ERROR DB FETCH MORE] {e}")
        finally:
            self._is_fetching = False  # BUKA GEMBOK

    def canFetchMore(self, parent=QModelIndex()):
        return not self.end_of_data

    def total_count(self):
        if not self.count_callback: return len(self.data_rows)
        try:
            res = self.count_callback(self.search_term)
            return int(res[0]) if isinstance(res, (tuple, list)) else int(res)
        except Exception:
            return len(self.data_rows)

    def get_all_data(self):
        return self.data_rows

    def set_fetch_callback(self, callback):
        self.fetch_callback = callback

    def set_count_callback(self, callback):
        self.count_callback = callback