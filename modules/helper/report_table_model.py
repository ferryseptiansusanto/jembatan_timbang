from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer
from modules.helper.konversidatetime import format_ts

class ReportTableModel(QAbstractTableModel):
    def __init__(self, headers, fetch_callback, count_callback=None, batch_size=100, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.batch_size = batch_size
        self.fetch_callback = fetch_callback
        self.count_callback = count_callback

        self.search_term = ""
        self.sort_column = None
        self.sort_order = Qt.AscendingOrder

        self.data_rows = []
        self.end_of_data = False

        self.fetchMore()

    def set_search_term(self, term):
        term = term.strip()
        if term != self.search_term:
            self.search_term = term
            self.reload()

    def rowCount(self, parent=QModelIndex()):
        return len(self.data_rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            row = index.row()
            col = index.column()
            try:
                value = self.data_rows[row][col]
                if col in [9, 10]:  # Tanggal Masuk / Keluar
                    return format_ts(value)
                if col in [6, 7, 8]:  # Gross, Tare, Netto
                    return "{:,.2f}".format(float(value))
                return str(value)
            except (IndexError, TypeError):
                print(f"[ERROR] data index out of bounds row={row} col={col}")
                return ""
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def canFetchMore(self, parent=QModelIndex()):
        if self.count_callback:
            return len(self.data_rows) < self.total_count()
        return not self.end_of_data

    def fetchMore(self, parent=QModelIndex()):
        if not self.fetch_callback:
            return
        offset = len(self.data_rows)
        rows = self.fetch_callback(
            offset,
            self.batch_size,
            self.search_term,
            self.sort_column,
            self.sort_order
        )
        if not rows:
            self.end_of_data = True
            return
        self.beginInsertRows(QModelIndex(), offset, offset + len(rows) - 1)
        self.data_rows.extend(rows)
        self.endInsertRows()

    def sort(self, column, order=Qt.AscendingOrder):
        self.sort_column = column
        self.sort_order = order
        self.reload()

    def reload(self):
        self.beginResetModel()
        self.data_rows.clear()
        self.end_of_data = False
        self.endResetModel()
        QTimer.singleShot(0, self.fetchMore)

    def total_count(self):
        if not self.count_callback:
            return len(self.data_rows)
        return self.count_callback(self.search_term)

    def get_all_data(self):
        return self.data_rows

    def set_fetch_callback(self, callback):
        self.fetch_callback = callback

    def set_count_callback(self, callback):
        self.count_callback = callback