DELETE FROM db_master_pemasok;
DELETE FROM db_master_pelanggan;
DELETE FROM sqlite_sequence WHERE name = 'db_master_pemasok';
DELETE FROM sqlite_sequence WHERE name = 'db_master_pelanggan';
INSERT INTO db_master_pemasok (nama, alamat, created_at, modified_at, created_by, modified_by, active)
VALUES ('Joseph', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Gary', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('John', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Eric', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('William', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Alice', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
  ('Mark', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Bob', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1);

INSERT INTO db_master_pelanggan (nama, alamat, created_at, modified_at, created_by, modified_by, active)
VALUES  ('Charlie', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Daisy', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Ethan', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Fiona', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Gabriel', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Hannah', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Ian', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Julia', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1),
 ('Kevin', 'SURABAYA', '2025-06-25 14:25:04', '2025-06-25 14:25:04',1,1,1);

