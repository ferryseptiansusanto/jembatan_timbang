# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_properties.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 700)
        self.btnSave = QtWidgets.QPushButton(Form)
        self.btnSave.setGeometry(QtCore.QRect(670, 30, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btnSave.setFont(font)
        self.btnSave.setObjectName("btnSave")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 661, 651))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(10, 180, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.edTelepon = QtWidgets.QLineEdit(self.tab)
        self.edTelepon.setGeometry(QtCore.QRect(170, 180, 391, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.edTelepon.setFont(font)
        self.edTelepon.setObjectName("edTelepon")
        self.txtedAlamat = QtWidgets.QTextEdit(self.tab)
        self.txtedAlamat.setGeometry(QtCore.QRect(170, 60, 391, 111))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.txtedAlamat.setFont(font)
        self.txtedAlamat.setObjectName("txtedAlamat")
        self.edNama = QtWidgets.QLineEdit(self.tab)
        self.edNama.setGeometry(QtCore.QRect(170, 10, 391, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.edNama.setFont(font)
        self.edNama.setObjectName("edNama")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(10, 60, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(10, 110, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.cbbComport = QtWidgets.QComboBox(self.tab_2)
        self.cbbComport.setGeometry(QtCore.QRect(180, 10, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbComport.setFont(font)
        self.cbbComport.setObjectName("cbbComport")
        self.cbbBaudrate = QtWidgets.QComboBox(self.tab_2)
        self.cbbBaudrate.setGeometry(QtCore.QRect(180, 60, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbBaudrate.setFont(font)
        self.cbbBaudrate.setObjectName("cbbBaudrate")
        self.cbbDatabits = QtWidgets.QComboBox(self.tab_2)
        self.cbbDatabits.setGeometry(QtCore.QRect(180, 110, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbDatabits.setFont(font)
        self.cbbDatabits.setObjectName("cbbDatabits")
        self.cbbStopbits = QtWidgets.QComboBox(self.tab_2)
        self.cbbStopbits.setGeometry(QtCore.QRect(180, 160, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbStopbits.setFont(font)
        self.cbbStopbits.setObjectName("cbbStopbits")
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(10, 160, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.cbbParity = QtWidgets.QComboBox(self.tab_2)
        self.cbbParity.setGeometry(QtCore.QRect(180, 210, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbParity.setFont(font)
        self.cbbParity.setObjectName("cbbParity")
        self.label_8 = QtWidgets.QLabel(self.tab_2)
        self.label_8.setGeometry(QtCore.QRect(10, 210, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.cbbFlowcontrol = QtWidgets.QComboBox(self.tab_2)
        self.cbbFlowcontrol.setGeometry(QtCore.QRect(180, 260, 251, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cbbFlowcontrol.setFont(font)
        self.cbbFlowcontrol.setObjectName("cbbFlowcontrol")
        self.label_9 = QtWidgets.QLabel(self.tab_2)
        self.label_9.setGeometry(QtCore.QRect(10, 260, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.btnRefresh = QtWidgets.QPushButton(self.tab_2)
        self.btnRefresh.setGeometry(QtCore.QRect(440, 10, 41, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btnRefresh.setFont(font)
        self.btnRefresh.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../resources/icon/refresh-icon-10846.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setObjectName("btnRefresh")
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.edNama, self.txtedAlamat)
        Form.setTabOrder(self.txtedAlamat, self.edTelepon)
        Form.setTabOrder(self.edTelepon, self.cbbComport)
        Form.setTabOrder(self.cbbComport, self.cbbBaudrate)
        Form.setTabOrder(self.cbbBaudrate, self.cbbDatabits)
        Form.setTabOrder(self.cbbDatabits, self.cbbStopbits)
        Form.setTabOrder(self.cbbStopbits, self.cbbParity)
        Form.setTabOrder(self.cbbParity, self.cbbFlowcontrol)
        Form.setTabOrder(self.cbbFlowcontrol, self.btnSave)
        Form.setTabOrder(self.btnSave, self.tabWidget)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btnSave.setText(_translate("Form", "Simpan"))
        self.label_3.setText(_translate("Form", "Telepon"))
        self.label_2.setText(_translate("Form", "Alamat Perusahaan"))
        self.label.setText(_translate("Form", "Nama Perusahaan"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Data Perusahaan"))
        self.label_4.setText(_translate("Form", "COM Port"))
        self.label_5.setText(_translate("Form", "Baud Rate"))
        self.label_6.setText(_translate("Form", "Data Bits"))
        self.label_7.setText(_translate("Form", "Stop Bits"))
        self.label_8.setText(_translate("Form", "Parity"))
        self.label_9.setText(_translate("Form", "Flow Control"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Port Setting"))
