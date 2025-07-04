# modules/helper/messagebox_utils.py
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

def show_info(parent, message, title="Informasi"):
    msg = QtWidgets.QMessageBox(parent)
    msg.setWindowFlags(Qt.Tool)  # Hindari suara sistem
    msg.setText(message)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.exec_()

def show_warning(parent, message, title="Peringatan"):
    msg = QtWidgets.QMessageBox(parent)
    msg.setWindowFlags(Qt.Tool)
    msg.setText(message)
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.exec_()

def show_question(parent, message, title="Konfirmasi"):
    msg = QtWidgets.QMessageBox(parent)
    msg.setWindowFlags(Qt.Tool)
    msg.setText(message)
    msg.setIcon(QtWidgets.QMessageBox.Question)
    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msg.setWindowTitle(title)
    return msg.exec_()