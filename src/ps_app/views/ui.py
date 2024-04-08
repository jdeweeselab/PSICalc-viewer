# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QStyle
from ps_app.views.tree_view import ApplicationWindow
import sys
import psicalc as pc
import pandas as pd
import os
import openpyxl
import pickle
import base64

pd.set_option('future.no_silent_downcasting', True)


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class Worker(QtCore.QThread):
    """The worker thread has signals for emitting
    output in realtime and a return object, which is
    the dictionary returned by psicalc. """

    outputSignal = QtCore.pyqtSignal(str)
    clusterSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.setTerminationEnabled()
        self.spread = None
        self.merged_data = None
        self.entropy = None

    def get_state(self):
        pc.return_dict_state()
        return

    def run(self):
        cluster_data = pc.find_clusters(self.spread, self.merged_data, "pairwise", self.entropy)
        self.clusterSignal.emit(cluster_data)

    def start_proc(self, spread,  merged_data, entropy):
        self.spread = spread
        self.merged_data = merged_data
        self.entropy = entropy
        self.start()


class LoadClusterWorker(QtCore.QThread):
    finished = QtCore.pyqtSignal(dict, pd.DataFrame, list, dict)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        wb = openpyxl.load_workbook(self.filename)
        encoded = ''.join(prop.value for prop in wb.custom_doc_props.props)
        data = pickle.loads(base64.b64decode(encoded))
        self.finished.emit(data['cluster_map'], data['msa'], data['low_entropy'], data['column_map'])


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("PSICalc Viewer")
        self.resize(960, 639)
        self.exiting = False
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self.thread = Worker()
        self.thread.clusterSignal.connect(self.return_dict)
        self.thread.finished.connect(self.returnUi)
        self.cluster_map = dict()
        self.files = list()
        self.labels = list()
        self.original_data = list()
        self.merged_msa = pd.DataFrame()
        self.column_map = dict()
        self.low_entropy = None

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setMinimumSize(QtCore.QSize(345, 599))
        self.widget_2.setMaximumSize(QtCore.QSize(345, 599))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout.addWidget(self.widget_2)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMinimumSize(QtCore.QSize(591, 599))
        self.widget.setMaximumSize(QtCore.QSize(591, 599))
        self.widget.setObjectName("widget")

        self.textBrowser = QtWidgets.QTextBrowser(self.widget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 10, 571, 200))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setStyleSheet("border: 1px solid; border-color: silver;"
                                       "border-radius:7px; background-color: palette(base); ")
        self.textEdit = QtWidgets.QPlainTextEdit(self.widget)
        self.textEdit.setReadOnly(True)
        self.textEdit.setGeometry(QtCore.QRect(0, 230, 571, 325))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setStyleSheet("border: 1px solid; border-color: silver;"
                                    " border-radius:7px; background-color: palette(base); ")
        self.editFont = QtGui.QFont()
        # self.font.setFamily(editor["editorFont"])
        self.editFont.setPointSize(12)
        self.textEdit.setFont(self.editFont)
        self.output = None
        self.process = QtCore.QProcess()
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)

        self.pushButton_2 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_2.setGeometry(QtCore.QRect(50, 150, 191, 32))
        self.pushButton_2.setObjectName("pushButton_2")

        self.checkBox = QtWidgets.QCheckBox(self.widget_2)
        self.checkBox.setGeometry(QtCore.QRect(40, 190, 301, 41))
        self.checkBox.setObjectName("checkBox")

        self.horizontalSlider = QtWidgets.QSlider(self.widget_2)
        self.horizontalSlider.setGeometry(QtCore.QRect(60, 420, 181, 20))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.spinBox = QtWidgets.QSpinBox(self.widget_2)
        self.spinBox.setGeometry(QtCore.QRect(90, 320, 42, 22))
        self.spinBox.setObjectName("spinBox")
        self.spinBox_2 = QtWidgets.QSpinBox(self.widget_2)
        self.spinBox_2.setGeometry(QtCore.QRect(80, 485, 42, 22))
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_2.setMinimum(1)
        self.spinBox_2.setValue(1)

        self.entropySpinBox = QtWidgets.QDoubleSpinBox(self.widget_2)
        self.entropySpinBox.setDecimals(2)
        self.entropySpinBox.setRange(0.0, 0.25)
        self.entropySpinBox.setFixedWidth(75)
        self.entropySpinBox.setSingleStep(0.01)
        self.entropySpinBox.setGeometry(QtCore.QRect(250, 485, 42, 22))
        self.entropySpinBox.setObjectName("entropySpinBox")

        self.label_2 = QtWidgets.QLabel(self.widget_2)
        self.label_2.setGeometry(QtCore.QRect(130, 235, 21, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.widget_2)
        self.label_3.setGeometry(QtCore.QRect(40, 260, 331, 31))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.widget_2)
        self.label_4.setGeometry(QtCore.QRect(70, 290, 191, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.widget_2)
        self.label_5.setGeometry(QtCore.QRect(50, 370, 291, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.widget_2)
        self.label_6.setGeometry(QtCore.QRect(140, 440, 16, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.widget_2)
        self.label_7.setGeometry(QtCore.QRect(160, 440, 31, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.widget_2)
        self.label_8.setGeometry(QtCore.QRect(60, 390, 141, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.widget_2)
        self.label_9.setGeometry(QtCore.QRect(20, 485, 91, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.widget_2)
        self.label_10.setGeometry(QtCore.QRect(150, 485, 42, 22))
        self.label_10.setObjectName("label_10")
        self.label_10.setFixedWidth(100)

        self.filesWidget = FilesWidget(self.widget_2, lambda files, labels: self.import_data(files, labels))
        self.filesWidget.setGeometry(QtCore.QRect(0, 0, 301, 145))

        self.pushButton_3 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 540, 151, 32))
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_4.setGeometry(QtCore.QRect(180, 540, 151, 32))
        self.pushButton_4.setObjectName("pushButton_4")

        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(380, 50, 111, 20))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.widget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")

        self.setCentralWidget(self.centralwidget)
        self.setStatusBar(self.statusbar)
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PsiCalc Viewer"))

        self.pushButton_2.setText(_translate("MainWindow", "Load Cluster Data"))
        self.pushButton_2.clicked.connect(self.load_cluster_data)

        self.checkBox.setText(_translate("MainWindow", "Label Using First Row Mapping"))
        self.checkBox.stateChanged.connect(self.if_button_checked)

        self.spinBox.valueChanged.connect(self.spinBox_handler)
        self.horizontalSlider.valueChanged.connect(self.horizontalSlider_handler)
        self.horizontalSlider.sliderReleased.connect(self.horizontalSlider_handler_2)

        self.label_2.setText(_translate("MainWindow", "OR"))
        self.label_3.setText(_translate("MainWindow", "Enter label number of actual location"))
        self.label_4.setText(_translate("MainWindow", "of first column in MSA"))
        self.label_5.setText(_translate("MainWindow", "Percentage of non-insertion data"))

        self.pushButton_3.setText(_translate("MainWindow", "Export MSA"))
        self.pushButton_3.clicked.connect(self.export_to_csv)

        self.pushButton_4.setText(_translate("MainWindow", "Submit"))
        try:
            self.pushButton_4.clicked.disconnect()
        except TypeError:
            pass
        self.pushButton_4.clicked.connect(self.submit_and_run)

        self.label_6.setText(_translate("MainWindow", "0"))
        self.label_7.setText(_translate("MainWindow", "%"))
        self.label_8.setText(_translate("MainWindow", "that must be present"))
        self.label_9.setText(_translate("MainWindow", "Spread:"))
        self.label_10.setText(_translate("MainWindow", "Entropy cutoff:"))

    def onReadyReadStandardOutput(self):
        result = self.process.readAllStandardOutput().data().decode()
        self.textEdit.appendPlainText(result)
        self.outputSignal.emit(result)

    def spinBox_handler(self):
        self.apply_transforms()

    def if_button_checked(self, state):
        if state == QtCore.Qt.Unchecked:
            self.spinBox.setEnabled(True)
        else:
            self.spinBox.setEnabled(False)

        self.apply_transforms()

    def apply_transforms(self):
        """
        Update saved dataframes based on all user settings
        """

        data = self.original_data.copy()
        if not data:
            return

        if self.checkBox.isChecked():
            data = [pc.deweese_schema(df, 'None') for df in data]
        else:
            data = [pc.durston_schema(df, self.spinBox.value()) for df in data]

        if self.horizontalSlider.value() > 0:
            data = self.remove_insertion_data(data, self.horizontalSlider.value())

        self.insert_to_window(data)

        self.merged_msa = pc.merge_sequences(data, self.labels)

    def horizontalSlider_handler(self):
        self.label_6.setText(str(self.horizontalSlider.value()))

    def horizontalSlider_handler_2(self):
        self.apply_transforms()

    # noinspection PyTypeChecker
    def remove_insertion_data(self, data: [pd.DataFrame], value):
        for i in range(len(data)):
            try:
                index_len = len(data[i].index)
                null_val = float(value) / 100
                data[i] = data[i].replace({'[-#?.]': None}, regex=True)
                labels_to_delete = []

                def series_remove_insertions(x):
                    non_nulls = x.count()
                    info_amount = non_nulls / index_len
                    if info_amount < null_val:
                        labels_to_delete.append(x.name)
                    return

                data[i].apply(series_remove_insertions, axis=0)
                data[i] = data[i].drop(labels_to_delete, axis=1)

            except IndexError or KeyError:
                self.insert_to_window("Not enough columns.")

        return data

    def import_data(self, files, labels):
        if not files:
            return

        self.files = files

        # If there's a single MSA, don't use the label
        if len(labels) == 1:
            self.labels = []
        else:
            self.labels = labels

        # Read all of the files and store in a list of dataframes
        data = []
        for filename in self.files:
            if str(filename).endswith((".txt", ".fasta")):
                df = pc.read_txt_file_format(filename)
                df = df.replace({'[-#?.]': None}, regex=True)
                data.append(df)
            else:
                df = pc.read_csv_file_format(filename)
                df = df.replace({'[-#?.]': None}, regex=True)
                data.append(df)

        self.original_data = data

        # Apply user settings to new data
        self.apply_transforms()

    def insert_to_window(self, args):
        self.textBrowser.clear()

        if isinstance(args, list):
            try:
                for i in range(len(args)):
                    if i < len(self.labels):
                        label = self.labels[i]
                    else:
                        label = ''
                    self.textBrowser.insertPlainText("File: " + self.files[i] + "\n" +
                                                     "Columns:  " + str(len(args[i].columns)) + "\n" +
                                                     "Sequences: " + str(len(args[i].index)) + "\n" +
                                                     "Labels: " + label + str(args[0].columns[0]) + "..."
                                                     + label + str(args[0].columns[-1])
                                                     + "\n\n")
            except IndexError:
                self.insert_to_window("Not enough columns to use.")
        elif isinstance(args, str):
            self.textBrowser.insertPlainText(args)

    def load_cluster_data(self):
        xls_file = QFileDialog.getOpenFileName(self, "Load cluster data from Excel", os.getenv('HOME'), 'Excel (*.xlsx)')[0]
        if not xls_file:
            return

        print(f"Loading cluster data from {xls_file}... ", end='')

        self.widget_2.setEnabled(False)
        self.load_cluster_worker = LoadClusterWorker(xls_file)
        self.load_cluster_worker.finished.connect(self.load_cluster_data_finished)
        self.load_cluster_worker.start()

    def load_cluster_data_finished(self, cluster_map, msa, low_entropy, column_map):
        print("done")
        self.w = ApplicationWindow(cluster_map, msa, low_entropy, column_map)
        self.w.show()
        self.widget_2.setEnabled(True)

    def export_to_csv(self):
        file = QFileDialog.getSaveFileName()
        save_file = str(file[0])
        self.merged_msa.to_csv(save_file, index=True, header=True)

    def normalOutputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    # noinspection PyCallByClass
    def submit_and_run(self):
        self.pushButton_4.clicked.disconnect()
        self.pushButton_4.clicked.connect(self.stop_process)
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pushButton_4.setText("Stop")
        self.spread = self.spinBox_2.value()
        self.entropy = self.entropySpinBox.value()
        # I believe this essentially needs to be intialized
        # and sent as data to a thread. No idea why I did it this way :/
        self.thread.start_proc(self.spread, self.merged_msa, self.entropy)

    def stop_process(self):
        """Halts the current process, returns the dictionary as is,
        quits, then waits for the thread to fully finish."""
        self.thread.get_state()

    def return_dict(self, r_dict):
        self.low_entropy = r_dict["low_entropy_sites"]
        del r_dict["low_entropy_sites"]
        self.column_map = r_dict["column_map"]
        del r_dict["column_map"]
        self.cluster_map = r_dict

    def returnUi(self):
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_4.setText("Submit")
        self.pushButton_4.clicked.disconnect()
        self.pushButton_4.clicked.connect(self.submit_and_run)
        self.w = ApplicationWindow(self.cluster_map, self.merged_msa, self.low_entropy, self.column_map)
        self.w.show()


class FilesWidget(QtWidgets.QWidget):
    def __init__(self, parent, callback):
        super().__init__(parent)

        self.change_callback = callback
        self.files = dict()
        self.prev_files = dict()

        # Build the table view
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(['Label', 'File', ''])
        self.table.setColumnWidth(0, self.table.fontMetrics().width('Label') + 10)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.table.itemChanged.connect(self.label_changed)

        # Add new rows
        self.add_button = QtWidgets.QPushButton('Add MSA file(s)...')
        self.add_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.add_button.clicked.connect(self.add_files)

        # Layout for table and button
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.add_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def add_files(self):
        label_gen = FilesWidget.label_gen()
        add_files = QFileDialog.getOpenFileNames()[0]

        # Make sure the files and labels are unique. Save in a dict[filename] = label
        for filename in add_files:
            if filename not in self.files:
                label = next(label_gen)
                used_labels = list(self.files.values())
                while label in used_labels:
                    label = next(label_gen)
                self.files[filename] = label

        # Repopulate the table
        self.redraw()

        # Save a copy in case we decide to revert later
        self.prev_files = self.files.copy()

        # Callback to the main window to update files and labels
        if add_files and self.change_callback:
            self.change_callback(list(self.files.keys()), list(self.files.values()))

    def label_changed(self, item):
        # Don't run this function for changes in here
        self.table.itemChanged.disconnect(self.label_changed)

        # Only for labels
        if item.column() == 0:
            new_label = item.text().strip()
            filename = self.table.item(item.row(), 1).data(QtCore.Qt.UserRole)

            # Make sure the user doesn't enter a dupilcate or empty label before updating
            if not new_label:
                QtWidgets.QMessageBox.warning(self, 'Error', "Labels can't be blank")
                item.setText(self.prev_files[filename])
            elif len(self.files) > 1 and new_label in self.files.values():
                QtWidgets.QMessageBox.warning(self, 'Error', "Labels must be unique")
                item.setText(self.prev_files[filename])
            else:
                self.files[filename] = new_label
                self.prev_files = self.files.copy()
                item.setToolTip(new_label)

                if self.change_callback:
                    self.change_callback(list(self.files.keys()), list(self.files.values()))

        self.table.itemChanged.connect(self.label_changed)

    def redraw(self):
        # Don't run this function for changes in here
        self.table.itemChanged.disconnect(self.label_changed)

        # Make a local copy and don't render a label if there's only one file
        files = self.files.copy()
        if len(self.files) == 1:
            files[list(files.keys())[0]] = ''

        # Clear the table
        self.table.setRowCount(0)
        for filename, label in files.items():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            label_item = QtWidgets.QTableWidgetItem(label)
            label_item.setToolTip(label)
            self.table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(label_item))

            # Uses just the file basename for display, but stores the full path for processing
            filename_item = QtWidgets.QTableWidgetItem(os.path.basename(filename))
            filename_item.setData(QtCore.Qt.UserRole, filename)
            filename_item.setToolTip(filename)
            filename_item.setFlags(filename_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.table.setItem(row_position, 1, filename_item)

            remove_button = QtWidgets.QPushButton()
            remove_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            remove_button.setStyleSheet("border: none;")
            remove_button.clicked.connect(self.remove_file)
            self.table.setCellWidget(row_position, 2, remove_button)

        self.table.itemChanged.connect(self.label_changed)

    def remove_file(self):
        # Get the button that was clicked
        remove_button = self.sender()
        if remove_button:
            row = self.table.indexAt(remove_button.pos()).row()
            del self.files[self.table.item(row, 1).data(QtCore.Qt.UserRole)]
            self.prev_files = self.files.copy()
            self.redraw()

            if self.change_callback:
                self.change_callback(list(self.files.keys()), list(self.files.values()))

    @staticmethod
    def label_gen():
        """
        Generator to create labels A-Z, AA-ZZ, etc
        """
        letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        labels = list(letters)
        while True:
            yield from labels
            labels = [a+b for a in labels for b in letters]
