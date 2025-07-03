DELETE FROM db_transaksi_pemasok;
DELETE FROM db_transaksi_pelanggan;
DELETE FROM sqlite_sequence WHERE name = 'db_transaksi_pemasok';
DELETE FROM sqlite_sequence WHERE name = 'db_transaksi_pelanggan';
INSERT INTO db_transaksi_pemasok (no_tiket, no_polisi, no_po_do, id_pelanggan, id_barang, nama_sopir,
                                  gross, tare, netto, tanggal_masuk,tanggal_keluar, keterangan,
                                  operator_timbang_masuk, operator_timbang_keluar, is_timbang, timbang1, timbang2)
VALUES ('TI001', 'L1111DA', 'DO001', 1, );
INSERT INTO db_transaksi_pelanggan (username, password, level, status, nama) VALUES ('ferry', 'e9087d0b20d80d3e12bc8530d883d7ad9c1eb3ebc5cb61824a2b460816503797', 'Administrator', 1, 'ferry');
