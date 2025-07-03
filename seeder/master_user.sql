DELETE FROM db_master_user;
DELETE FROM sqlite_sequence WHERE name = 'db_master_user';
INSERT INTO db_master_user (username, password, level, status, nama) VALUES ('superadmin', 'c9758c85d0756cefa13438a53a9f98288ca048b12d7935cca9616076de9cf9da', 'SuperAdmin', 1, 'Super Admin');
INSERT INTO db_master_user (username, password, level, status, nama) VALUES ('ferry', 'e9087d0b20d80d3e12bc8530d883d7ad9c1eb3ebc5cb61824a2b460816503797', 'Administrator', 1, 'ferry');
