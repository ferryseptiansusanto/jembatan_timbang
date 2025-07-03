from PyQt5.QtWidgets import QLabel, QWidget
from customwidgets.switch_mode.switch_mode_form import SwitchButton


class SwitchMode:
    def __init__(self, label_widget: QLabel, container_widget: QWidget,
                 on_text="Aktif", off_text="Nonaktif", start_flag=False, callback=None):
        self.label_widget = label_widget
        self.container_widget = container_widget
        self.on_text = on_text
        self.off_text = off_text
        self.callback = callback

        self.switch = SwitchButton()
        self.switch.setChecked(start_flag)
        self.switch.toggled.connect(self.toggle_handler)

        self.container_widget.layout().addWidget(self.switch)
        self.update_label(start_flag)

    def toggle_handler(self, checked):
        self.update_label(checked)
        if self.callback:
            self.callback(checked)

    def update_label(self, checked):
        text = self.on_text if checked else self.off_text
        self.label_widget.setText(text)

    def set_checked(self, checked):
        self.switch.setChecked(checked)

    def is_checked(self):
        return self.switch.isChecked()