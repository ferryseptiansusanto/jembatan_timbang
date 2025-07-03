from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty,pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush

import sys

class SwitchButton(QWidget):
    toggled = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._position = 0
        self.setFixedSize(60, 28)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self._animation = QPropertyAnimation(self, b"position", self)
        self._animation.setDuration(120)
        self.setProperty("checked", False)


    def isChecked(self):
        return self.property("checked")

    def setChecked(self, checked):
        self.setProperty("checked", checked)
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(1 if checked else 0)
        self._animation.start()
        self.update()

    def toggle(self):
        self.setChecked(not self.isChecked())
        self.toggled.emit(self.isChecked())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        radius = self.height() / 2
        thumb_radius = radius - 4
        track_color = QColor(0, 180, 0) if self.isChecked() else QColor(180, 180, 180)
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), radius, radius)
        x = 4 + (self.width() - 2 * thumb_radius - 8) * self._position
        p.setBrush(QColor("white"))
        p.drawEllipse(int(x), 4, int(thumb_radius * 2), int(thumb_radius * 2))

    def get_position(self):
        return self._position

    def set_position(self, pos):
        self._position = pos
        self.update()

    position = pyqtProperty(float, get_position, set_position)


class SwitchModeForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Toggle Mode")
        self.mode_label = QLabel("Mode Input : Pemasok")

        self.switch = SwitchButton()
        self.switch.setChecked(False)
        self.switch.toggled.connect(self.on_toggle_mode)

        layout = QHBoxLayout()
        layout.addWidget(self.mode_label)
        layout.addWidget(self.switch)

        wrapper = QVBoxLayout()
        wrapper.addLayout(layout)
        self.setLayout(wrapper)

    def on_toggle_mode(self, checked):
        mode = "Pelanggan" if checked else "Pemasok"
        self.mode_label.setText(f"Mode Input : {mode}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SwitchModeForm()
    window.show()
    sys.exit(app.exec_())