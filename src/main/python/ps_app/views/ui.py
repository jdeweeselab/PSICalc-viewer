# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QStyle
from ps_app.views.tree_view import ApplicationWindow
import gc
import sys
import psicalc as pc
import pandas as pd


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

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.setTerminationEnabled()
        self.cluster_data = dict()
        self.spread, self.df = None, None

    def get_state(self):
        dict_state = pc.return_dict_state()
        return dict_state

    def run(self):
        self.cluster_data = pc.find_clusters(self.spread, self.df)
        self.clusterSignal.emit(self.cluster_data)

    def start_proc(self, spread, df):
        self.spread = spread
        self.df = df
        self.start()


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, csv_img):
        super().__init__()
        self.setObjectName("PSICalc Viewer")
        self.resize(960, 639)
        self.exiting = False
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)
        self.thread = Worker()
        self.thread.clusterSignal.connect(self.return_dict)
        self.thread.finished.connect(self.returnUi)
        self.filename = str()
        self.cluster_map = dict()
        self.df = pd.DataFrame()
        self.df_stack = [self.df.copy(deep=True)]
        self.is_modified = False

        self.csv_img = csv_img
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
        self.textBrowser.setGeometry(QtCore.QRect(0, 55, 571, 150))
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

        self.pushButton = QtWidgets.QPushButton(self.widget_2)
        self.pushButton.setGeometry(QtCore.QRect(20, 40, 181, 31))
        self.pushButton.setObjectName("pushButton")

        self.pushButton_2 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 140, 191, 31))
        self.pushButton_2.setObjectName("pushButton_2")

        self.checkBox = QtWidgets.QCheckBox(self.widget_2)
        self.checkBox.setGeometry(QtCore.QRect(20, 190, 301, 41))
        self.checkBox.setObjectName("checkBox")

        self.horizontalSlider = QtWidgets.QSlider(self.widget_2)
        self.horizontalSlider.setGeometry(QtCore.QRect(30, 420, 181, 20))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.spinBox = QtWidgets.QSpinBox(self.widget_2)
        self.spinBox.setGeometry(QtCore.QRect(90, 320, 42, 22))
        self.spinBox.setObjectName("spinBox")
        self.spinBox_2 = QtWidgets.QSpinBox(self.widget_2)
        self.spinBox_2.setGeometry(QtCore.QRect(90, 485, 42, 22))
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_2.setMinimum(2)
        self.spinBox_2.setValue(7)

        self.label_2 = QtWidgets.QLabel(self.widget_2)
        self.label_2.setGeometry(QtCore.QRect(100, 230, 21, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.widget_2)
        self.label_3.setGeometry(QtCore.QRect(20, 260, 331, 31))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.widget_2)
        self.label_4.setGeometry(QtCore.QRect(50, 290, 191, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.widget_2)
        self.label_5.setGeometry(QtCore.QRect(30, 370, 291, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.widget_2)
        self.label_6.setGeometry(QtCore.QRect(100, 440, 16, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.widget_2)
        self.label_7.setGeometry(QtCore.QRect(120, 440, 31, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.widget_2)
        self.label_8.setGeometry(QtCore.QRect(60, 390, 141, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.widget_2)
        self.label_9.setGeometry(QtCore.QRect(30, 485, 91, 16))
        self.label_9.setObjectName("label_9")

        self.lineEdit = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit.setGeometry(QtCore.QRect(20, 90, 301, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setStyleSheet("border: 1px solid; border-color: silver;"
                                    " border-radius:3px; background-color: palette(base); ")

        self.pushButton_3 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 540, 151, 31))
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_4.setGeometry(QtCore.QRect(180, 540, 151, 31))
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

        self.pushButton.setText(_translate("MainWindow", "Select File for Upload"))
        self.pushButton.clicked.connect(self.select_file_for_upload)
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
        self.pushButton_4.clicked.connect(self.submit_and_run)

        self.label_6.setText(_translate("MainWindow", "0"))
        self.label_7.setText(_translate("MainWindow", "%"))
        self.label_8.setText(_translate("MainWindow", "that must be present"))
        self.label_9.setText(_translate("MainWindow", "Spread:"))

    def onReadyReadStandardOutput(self):
        result = self.process.readAllStandardOutput().data().decode()
        self.textEdit.appendPlainText(result)
        self.outputSignal.emit(result)

    def pushButton_handler(self):
        self.open_dialog_box()

    def spinBox_handler(self):
        if not self.checkBox.isChecked():
            self.df = pc.durston_schema(self.df, self.spinBox.value())
            self.insert_to_window(self.df)
            self.df_stack.pop(0)
            self.df_stack.append(self.df.copy(deep=True))
            self.is_modified = True
        else:
            self.textBrowser.clear()
            self.textBrowser.insertPlainText("Error: Cannot change label number while box is checked.")

    def horizontalSlider_handler(self):
        self.label_6.setText(str(self.horizontalSlider.value()))
        self.insert_to_window("Loading...")

    def horizontalSlider_handler_2(self):
        stack_copy = self.df_stack[0]
        if not stack_copy.empty:
            self.df = self.remove_insertion_data(stack_copy, self.horizontalSlider.value())
            self.insert_to_window(self.df)
        else:
            self.textBrowser.clear()
            self.textBrowser.insertPlainText("Error: Please select a labelling option first.")

    # noinspection PyTypeChecker
    def remove_insertion_data(self, df: pd.DataFrame, value):
        try:
            index_len = len(df.index)
            null_val = float(value) / 100
            #df = df.replace({'[-#?.]': None}, regex=True)
            labels_to_delete = []

            def series_remove_insertions(x):
                non_nulls = x.count()
                info_amount = non_nulls / index_len
                if info_amount < null_val:
                    labels_to_delete.append(x.name)
                return

            df.apply(series_remove_insertions, axis=0)

            df = df.drop(labels_to_delete, axis=1)

        except IndexError or KeyError:
            self.insert_to_window("Not enough columns.")

        return df

    def open_dialog_box(self):
        self.filename = QFileDialog.getOpenFileName()[0]
        self.lineEdit.insert(self.filename)
        return self.filename

    def import_data(self):
        if str(self.filename).endswith(".txt"):
            self.df = pc.read_txt_file_format(self.filename)
        else:
            self.df = pc.read_csv_file_format(self.filename)
        self.df = self.df.replace({'[-#?.]': None}, regex=True)
        self.insert_to_window(self.df)

    def insert_to_window(self, args):
        self.textBrowser.clear()
        if isinstance(args, pd.DataFrame):
            try:
                self.textBrowser.insertPlainText("Columns:  " + str(len(self.df.columns)) + "\n" +
                                                 "Sequences: " + str(len(self.df.index)) + "\n" +
                                                 "Label Numbers: "
                                                 + str(args.columns[0]) + "..." + str(args.columns[-1]))
            except IndexError:
                self.insert_to_window("Not enough columns to use.")
        elif isinstance(args, str):
            self.textBrowser.insertPlainText(args)

    def select_file_for_upload(self):
        self.pushButton_handler()
        self.import_data()

    def load_cluster_data(self):
        self.pushButton_handler()
        self.win = ApplicationWindow(self.filename, self.csv_img)
        self.win.show()

    def garbage_collect(self, df: pd.DataFrame):
        del df
        gc.collect()
        self.import_data()

    def if_button_checked(self):
        if self.checkBox.isChecked():
            if self.is_modified:
                self.garbage_collect(self.df)
            self.df = pc.deweese_schema(self.df, 'None')
            self.insert_to_window(self.df)
            self.df_stack.pop(0)
            self.df_stack.append(self.df.copy(deep=True))
        if not self.checkBox.isChecked():
            self.garbage_collect(self.df)

    def export_to_csv(self):
        file = QFileDialog.getSaveFileName()
        save_file = str(file[0])
        self.df.to_csv(save_file, index=True, header=True)

    def normalOutputWritten(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    # noinspection PyCallByClass
    def submit_and_run(self):
        self.pushButton_4.clicked.connect(self.stop_process)
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.pushButton_4.setText("Stop")
        self.spread = self.spinBox_2.value()
        # long running process
        self.df = self.df.replace({None: '-'})
        self.thread.start_proc(self.spread, self.df)

    def stop_process(self):
        """Halts the current process, returns the dictionary as is,
        quits, then waits for the thread to fully finish."""
        self.cluster_map = self.thread.get_state()
        self.returnUi()
        self.pushButton_4.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.pushButton_4.setText("Submit")
        self.pushButton_4.clicked.connect(self.submit_and_run)

    def return_dict(self, r_dict):
        self.cluster_map = r_dict

    def returnUi(self):
        self.w = ApplicationWindow(self.cluster_map, self.csv_img)
        self.w.show()


