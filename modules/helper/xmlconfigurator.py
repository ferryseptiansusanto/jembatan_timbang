import os
import xml.etree.ElementTree as ET
from modules.config.config import get_config_path


def baca_konfigurasi():
    """
    Membaca file XML dan mengembalikan dictionary konfigurasi.
    """
    filepath = get_config_path()

    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return {}

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        return {
            "nama_perusahaan": root.findtext("nama_perusahaan", ""),
            "alamat": root.findtext("alamat", ""),
            "telepon": root.findtext("telepon", ""),
            "comport": root.findtext("comport", ""),
            "baudrate": root.findtext("baudrate", ""),
            "databits": root.findtext("databits", ""),
            "stopbits": root.findtext("stopbits", ""),
            "parity": root.findtext("parity", ""),
            "flowcontrol": root.findtext("flowcontrol", "")
        }
    except ET.ParseError:
        return {}


def tulis_konfigurasi(data):
    """
    Menyimpan konfigurasi ke file XML.
    """
    filepath = get_config_path()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    root = ET.Element("konfigurasi")

    for key, value in data.items():
        element = ET.SubElement(root, key)
        element.text = value

    tree = ET.ElementTree(root)
    try:
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        raise IOError(f"Gagal menyimpan konfigurasi ke XML:\n{e}")

def bacaslipxml():
    """
    Mengambil isi template slip transaksi dari elemen <template_slip_html> dalam config XML.
    """
    filepath = get_config_path()

    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return ""

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        node = root.find("template_slip_html")
        return node.text.strip() if node is not None and node.text else ""
    except ET.ParseError:
        return ""

def tulis_slipxml(template_str):
    """
    Menyimpan template slip HTML ke elemen <template_slip_html> dalam config XML.
    """
    filepath = get_config_path()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Baca konfigurasi lama (jika ada)
    try:
        if os.path.exists(filepath):
            tree = ET.parse(filepath)
            root = tree.getroot()
        else:
            root = ET.Element("konfigurasi")
            tree = ET.ElementTree(root)

        node = root.find("template_slip_html")
        if node is None:
            node = ET.SubElement(root, "template_slip_html")

        node.text = template_str

        tree.write(filepath, encoding="utf-8", xml_declaration=True)
    except ET.ParseError:
        raise IOError("Format XML tidak valid. Gagal menyimpan template slip.")
