from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

class CheckBoxSqlTableModel(QSqlTableModel):
    def __init__(self, checkbox_column=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkbox_column = checkbox_column  # ← index kolom checkbox

    def data(self, index, role=Qt.DisplayRole):
        if index.column() == self.checkbox_column:
            if role == Qt.CheckStateRole:
                value = super().data(index, Qt.DisplayRole)
                return Qt.Checked if value else Qt.Unchecked
            if role == Qt.DisplayRole:
                return ""  # Jangan tampilkan angka 1/0
        return super().data(index, role)

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == self.checkbox_column:
            flags |= Qt.ItemIsEditable #Qt.ItemIsUserCheckable |
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if index.column() == self.checkbox_column and role == Qt.CheckStateRole:
            return super().setData(index, 1 if value == Qt.Checked else 0, Qt.EditRole)
        return super().setData(index, value, role)