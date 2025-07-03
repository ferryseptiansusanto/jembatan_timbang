import hashlib
from modules.helper.db import execute_scalar, execute_query

def initialize_superuser():
    user_count = execute_scalar("SELECT COUNT(*) FROM db_master_user")

    if user_count == 0:
        print("Database kosong. Menambahkan user SuperAdmin default...")

        default_username = "superadmin"
        default_password = "superadminferry"  # bisa diganti di sini
        hashed_password = hashlib.sha256(default_password.encode()).hexdigest()

        execute_query("""
            INSERT INTO db_master_user (username, password, level, status, nama)
            VALUES (?, ?, ?, ?, ?)
        """, (default_username, hashed_password, "SuperAdmin", 1, "Super Admin"))

        print(f"✅ SuperAdmin berhasil dibuat. Username: {default_username}, Password: {default_password}")
    else:
        print("Database sudah memiliki user. Tidak ada perubahan.")