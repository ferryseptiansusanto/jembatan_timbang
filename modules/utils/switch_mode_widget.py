from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty,pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush


class SwitchModeWidget(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, on_text="Aktif", off_text="Nonaktif", start_flag=False, callback=None, parent=None):
        super().__init__(parent)

        self.on_text = on_text
        self.off_text = off_text
        self.callback = callback

        self.label = QLabel()
        self.switch = SwitchButton()
        self.switch.setChecked(start_flag)

        self._setup_layout()
        self._update_label(start_flag)

        self.switch.toggled.connect(self._handle_toggle)

        # Optional: forward signal to external handler
        if self.callback:
            self.toggled.connect(self.callback)

    def _setup_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Atur gaya dan alignment label dulu
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.label.setMinimumWidth(100)
        # self.label.setStyleSheet("padding-left: 10px; font-weight: bold; font-size: 10pt; color: #000;")

        # Tambahkan ke layout
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.switch)

        self.setLayout(layout)

    def _handle_toggle(self, checked):
        self._update_label(checked)
        self.toggled.emit(checked)

    def _update_label(self, checked):
        self.label.setText(self.on_text if checked else self.off_text)

    def is_checked(self):
        return self.switch.isChecked()

    def set_checked(self, checked):
        self.switch.setChecked(checked)

    def set_callback(self, func):
        self.toggled.disconnect()
        self.toggled.connect(func)



class SwitchButton(QWidget):
    toggled = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._position = 0
        self.setFixedSize(50, 28)
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
