BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "db_master_barang" (
	"id"	INTEGER,
	"namabarang"	TEXT UNIQUE,
	"kategori"	TEXT,
	"created_date"	INTEGER,
	"modified_date"	INTEGER,
	"created_by"	INTEGER,
	"modified_by"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "db_master_pelanggan" (
	"id"	INTEGER,
	"nama"	TEXT UNIQUE,
	"alamat"	TEXT,
	"created_at"	INTEGER,
	"modified_at"	INTEGER,
	"created_by"	INTEGER,
	"modified_by"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "db_master_pemasok" (
	"id"	INTEGER,
	"nama"	TEXT UNIQUE,
	"alamat"	TEXT,
	"created_at"	INTEGER,
	"modified_at"	INTEGER,
	"created_by"	INTEGER,
	"modified_by"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "db_master_user" (
	"id"	INTEGER,
	"username"	TEXT UNIQUE,
	"password"	TEXT,
	"level"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "db_properties" (
	"id"	INTEGER,
	"nama_perusahaan"	TEXT UNIQUE,
	"alamat"	TEXT,
	"telepon"	TEXT,
	"comport"	TEXT,
	"baudrate"	TEXT,
	"databits"	TEXT,
	"stopbits"	TEXT,
	"parity"	TEXT,
	"flowcontrol"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "db_transaksi_pelanggan" (
	"id"	INTEGER,
	"no_tiket"	TEXT,
	"no_polisi"	TEXT,
	"no_po_do"	TEXT,
	"id_pelanggan"	INTEGER,
	"id_barang"	INTEGER,
	"nama_sopir"	TEXT,
	"gross"	NUMERIC,
	"tare"	NUMERIC,
	"netto"	NUMERIC,
	"tanggal_masuk"	INTEGER,
	"tanggal_keluar"	INTEGER,
	"keterangan"	TEXT,
	"operator_timbang_masuk"	INTEGER,
	"operator_timbang_keluar"	INTEGER,
	"is_timbang"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_barang") REFERENCES "db_master_barang"("id"),
	FOREIGN KEY("id_pelanggan") REFERENCES "db_master_pelanggan"("id")
);
CREATE TABLE IF NOT EXISTS "db_transaksi_pemasok" (
	"id"	INTEGER,
	"no_tiket"	TEXT,
	"no_polisi"	TEXT,
	"no_po_do"	TEXT,
	"id_pemasok"	INTEGER,
	"id_barang"	INTEGER,
	"nama_sopir"	TEXT,
	"gross"	NUMERIC,
	"tare"	NUMERIC,
	"netto"	NUMERIC,
	"tanggal_masuk"	INTEGER,
	"tanggal_keluar"	INTEGER,
	"keterangan"	TEXT,
	"operator_timbang_masuk"	INTEGER,
	"operator_timbang_keluar"	INTEGER,
	"is_timbang"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_barang") REFERENCES "db_master_barang"("id"),
	FOREIGN KEY("id_pemasok") REFERENCES "db_master_pemasok"("id")
);
CREATE TABLE IF NOT EXISTS "sqlite_stat4" (
	"tbl"	,
	"idx"	,
	"neq"	,
	"nlt"	,
	"ndlt"	,
	"sample"	
);
COMMIT;
