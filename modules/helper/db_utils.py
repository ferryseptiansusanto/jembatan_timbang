import sqlite3
import zipfile
from datetime import datetime
from tqdm import tqdm
import os

def backup_sqlite_to_zip(db_path, output_dir):
    """
    Backup database SQLite ke file .sql dan kompresi .zip berisi INSERT INTO statements saja.
    Returns path file ZIP.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sql_filename = f"backup_{timestamp}.sql"
    sql_path = os.path.join(output_dir, sql_filename)
    zip_path = os.path.join(output_dir, f"backup_{timestamp}.zip")

    try:
        conn = sqlite3.connect(db_path)
        inserts = [line for line in conn.iterdump() if line.startswith("INSERT INTO")]
        conn.close()

        with open(sql_path, 'w', encoding='utf-8') as f:
            for line in tqdm(inserts, desc="🔄 Membackup database", unit="baris", leave=False):
                f.write(f"{line}\n")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sql_path, os.path.basename(sql_path))
        os.remove(sql_path)

        return zip_path
    except Exception as e:
        raise RuntimeError(f"Backup gagal: {str(e)}")

def restore_sqlite_from_zip(zip_path, db_path):
    """
    Restore isi file ZIP berisi file .sql ke SQLite database.
    Menghapus temp file setelah restore selesai.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError("File ZIP tidak ditemukan")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            sql_files = [name for name in zipf.namelist() if name.endswith(".sql")]
            if not sql_files:
                raise Exception("File .sql tidak ditemukan di dalam zip.")
            zipf.extract(sql_files[0], "temp_restore/")
            sql_path = os.path.join("temp_restore", sql_files[0])

        with sqlite3.connect(db_path) as conn:
            with open(sql_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())

        os.remove(sql_path)
        os.rmdir("temp_restore")
    except Exception as e:
        raise RuntimeError(f"Restore gagal: {str(e)}")