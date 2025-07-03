from PyQt5.QtCore import QObject, pyqtSignal, QThread
import serial
import time

class SerialWorker(QObject):
    data_received = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, port, baudrate=9600, timeout=1, **kwargs):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.kwargs = kwargs
        self._running = False
        self.ser = None

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout, **self.kwargs)
            self._running = True
            while self._running:
                if self.ser and self.ser.is_open:
                    raw = self.ser.readline()
                    if raw:
                        try:
                            text = raw.decode(errors="ignore").strip()
                            if text:
                                self.data_received.emit(text)
                        except Exception as e:
                            self.error.emit(f"[Decode Error] {e}")
                    else:
                        time.sleep(0.01)
                else:
                    break
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.finished.emit()

    def stop(self):
        self._running = False