from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal
from modules.helper.serialworker import SerialWorker
from modules.config.config import map_parity, map_stopbits, map_bytesize
from modules.helper.xmlconfigurator import baca_konfigurasi

class SerialManager(QObject):
    data_received = pyqtSignal(str)
    status_changed = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.thread = None
        self._is_stopping = False

        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(3000)  # 3 detik
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)
        self.config = baca_konfigurasi()

    def start(self):
        if self.thread and self.thread.isRunning():
            print("[WARN] Thread sudah aktif, tidak akan restart.")
            return

        if not self.config:
            print("[ERROR] Konfigurasi COM tidak ditemukan.")
            return

        self._setup_worker_thread()
        self.thread.start()
        self.status_changed.emit(self.config["comport"], True)

    def _setup_worker_thread(self):
        self.worker = SerialWorker(
            port=self.config.get("comport", ""),
            baudrate=self.config.get("baudrate", 9600),
            parity=map_parity(self.config.get("parity", "N")),
            stopbits=map_stopbits(self.config.get("stopbits", 1)),
            bytesize=map_bytesize(self.config.get("databits", 8))
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)
        self.worker.data_received.connect(self._handle_data)
        self.worker.finished.connect(self.on_finished)

    def _handle_data(self, data):
        self.data_received.emit(data)

    def on_finished(self):
        print("[INFO] Worker selesai.")

        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            self.thread = None
        else:
            print("[WARN] Thread sudah selesai atau None.")

        self.status_changed.emit("", False)

        if not self._is_stopping:
            print("[INFO] Menjadwalkan reconnect...")
            self.reconnect_timer.start()
        else:
            print("[INFO] Stop manual, tidak akan reconnect.")
            self._is_stopping = False

    def _attempt_reconnect(self):
        print("[INFO] Mencoba reconnect COM port...")
        self.start()

    def stop(self):
        self._is_stopping = True  # tandai manual stop

        if self.worker:
            self.worker.stop()
            self.worker = None

        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            self.thread = None

        self.status_changed.emit("", False)
        self.reconnect_timer.stop()