DELETE FROM db_master_barang;
DELETE FROM sqlite_sequence WHERE name = 'db_master_barang';

INSERT INTO db_master_barang (namabarang, kategori, created_date, modified_date, created_by, modified_by, active)
VALUES ('BATU PECAH', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1),
       ('ABU BATU 0-5', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1),
       ('BATU 5-10', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1),
       ('BATU 18-24', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1),
       ('BATU 2-3', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1),
       ('PASIR', 'MATERIAL', '2025-06-25 14:25:04', '2025-06-25 14:41:46', 'ferry', 'ferry', 1);

