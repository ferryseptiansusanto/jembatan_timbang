-- we don't know how to generate root <with-no-name> (class Root) :(
create table db_master_barang
(
    id            INTEGER
        primary key autoincrement,
    namabarang    TEXT
        unique,
    kategori      TEXT,
    created_date  INTEGER,
    modified_date INTEGER,
    created_by    INTEGER,
    modified_by   INTEGER,
    status        integer
);

create table db_master_pelanggan
(
    id          INTEGER
        primary key autoincrement,
    nama        TEXT
        unique,
    alamat      TEXT,
    created_at  INTEGER,
    modified_at INTEGER,
    created_by  INTEGER,
    modified_by INTEGER,
    status      integer
);

create table db_master_pemasok
(
    id          INTEGER
        primary key autoincrement,
    nama        TEXT
        unique,
    alamat      TEXT,
    created_at  INTEGER,
    modified_at INTEGER,
    created_by  INTEGER,
    modified_by INTEGER,
    status      INTEGER
);

create table db_master_user
(
    id       INTEGER
        primary key autoincrement,
    username TEXT
        unique,
    password TEXT,
    level    TEXT,
    status   integer,
    nama     text
);

create table db_properties
(
    id              INTEGER
        primary key autoincrement,
    nama_perusahaan TEXT
        unique,
    alamat          TEXT,
    telepon         TEXT,
    comport         TEXT,
    baudrate        TEXT,
    databits        TEXT,
    stopbits        TEXT,
    parity          TEXT,
    flowcontrol     TEXT
);

create table db_transaksi_pelanggan
(
    id                      INTEGER
        primary key autoincrement,
    no_tiket                TEXT,
    no_polisi               TEXT,
    no_po_do                TEXT,
    id_pelanggan            INTEGER
        references db_master_pelanggan,
    id_barang               INTEGER
        references db_master_barang,
    nama_sopir              TEXT,
    gross                   NUMERIC,
    tare                    NUMERIC,
    netto                   NUMERIC,
    tanggal_masuk           INTEGER,
    tanggal_keluar          INTEGER,
    keterangan              TEXT,
    operator_timbang_masuk  INTEGER,
    operator_timbang_keluar INTEGER,
    is_timbang              INTEGER,
    timbang1                NUMERIC,
    timbang2                NUMERIC
);

create table db_transaksi_pemasok
(
    id                      INTEGER
        primary key autoincrement,
    no_tiket                TEXT,
    no_polisi               TEXT,
    no_po_do                TEXT,
    id_pemasok              INTEGER
        references db_master_pemasok,
    id_barang               INTEGER
        references db_master_barang,
    nama_sopir              TEXT,
    gross                   NUMERIC,
    tare                    NUMERIC,
    netto                   NUMERIC,
    tanggal_masuk           INTEGER,
    tanggal_keluar          INTEGER,
    keterangan              TEXT,
    operator_timbang_masuk  INTEGER,
    operator_timbang_keluar INTEGER,
    is_timbang              INTEGER,
    timbang1                NUMERIC,
    timbang2                NUMERIC
);

