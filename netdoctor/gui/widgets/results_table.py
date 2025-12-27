"""
Custom QTableView model for displaying results.
"""

from PySide6.QtWidgets import QTableView
from PySide6.QtCore import QAbstractTableModel, Qt
from typing import List, Dict, Any


class ResultsTableModel(QAbstractTableModel):
    """Table model for displaying scan results."""

    def __init__(self, headers: List[str], parent=None):
        super().__init__(parent)
        self.headers = headers
        self.data_rows: List[Dict[str, Any]] = []

    def rowCount(self, parent=None):
        return len(self.data_rows)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = self.data_rows[index.row()]
            col_name = self.headers[index.column()]
            value = row.get(col_name, "")
            return str(value) if value is not None else ""

        return None

    def add_row(self, row_data: Dict[str, Any]):
        """Add a row to the model."""
        self.beginInsertRows(self.index(len(self.data_rows), 0), len(self.data_rows), len(self.data_rows))
        self.data_rows.append(row_data)
        self.endInsertRows()

    def clear(self):
        """Clear all rows."""
        self.beginResetModel()
        self.data_rows.clear()
        self.endResetModel()

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all data rows."""
        return self.data_rows.copy()


class ResultsTableView(QTableView):
    """TableView widget for displaying results."""

    def __init__(self, headers: List[str], parent=None):
        super().__init__(parent)
        self.model = ResultsTableModel(headers, self)
        self.setModel(self.model)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
