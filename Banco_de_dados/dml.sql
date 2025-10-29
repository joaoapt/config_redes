use redes_db;

INSERT INTO device_tb (nm_hostname, nm_fabriante, ip_address, dt_password, dt_device)
VALUES ('Router01', 'Cisco', '192.168.1.1', TRUE, NOW());



SELECT * FROM device_tb;
SELECT * FROM device_tb WHERE nm_hostname = 'Router01';


INSERT INTO backup_tb (device_id, sp_backup, dt_backup)
VALUES (1, 'Backup da config inicial', NOW());

DELETE FROM backup_tb WHERE id_backup = 1;

SELECT * FROM backup_tb;
SELECT * FROM backup_tb WHERE device_id = 1;


INSERT INTO config_tb (device_id, sp_config, dt_config)
VALUES (1, 'Configuração inicial aplicada', NOW());

DELETE FROM config_tb WHERE id_config = 1;

SELECT * FROM config_tb;
SELECT * FROM config_tb WHERE device_id = 1;

DELETE FROM device_tb WHERE id_device = 1;

select * from device_tb;
SELECT * FROM config_tb;
SELECT * FROM backup_tb;