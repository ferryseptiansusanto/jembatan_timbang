from modules.helper.xmlconfigurator import baca_konfigurasi

class CompanyProfile:
    def __init__(self):
        config = baca_konfigurasi() or {}
        self.nama = config.get("nama_perusahaan", "Perusahaan")
        self.alamat = config.get("alamat", "")
        self.telepon = config.get("telepon", "")

    def full_address(self):
        return f"{self.nama}\n{self.alamat}\nTelp: {self.telepon}"