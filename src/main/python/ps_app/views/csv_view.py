import os
import csv
from PyQt5 import QtWidgets


class ClusterData(QtWidgets.QTableWidget):
    def __init__(self, path):
        super().__init__()
        self.setRowCount(0)
        self.setColumnCount(3)
        self.path = path
        if type(self.path) is dict:
            file = [[str(k), str(v[0]), str(v[1])] for k, v in self.path.items()]
            file.insert(0, ['Cluster', 'SR Mode', 'Discovered'])
        else:
            data = open(self.path)
            file = csv.reader(data)

        for row_data in file:
            row = self.rowCount()
            self.insertRow(row)
            for col, each in enumerate(row_data):
                entry = row_data[col]
                item = QtWidgets.QTableWidgetItem(entry)
                self.setItem(row, col, item)

    def save_sheet(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", os.getenv('HOME'), 'CSV (*.csv)')
        if path[0] != '':
            with open(path[0], "w") as csv_file:
                writer = csv.writer(csv_file)
                for row in range(self.rowCount()):
                    row_data = []
                    for column in range(self.columnCount()):
                        item = self.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    writer.writerow(row_data)
