DROP DATABASE IF EXISTS redes_db;
CREATE DATABASE redes_db;
USE redes_db;

CREATE TABLE device_tb (
    id_device INT AUTO_INCREMENT PRIMARY KEY,
    nm_hostname  VARCHAR(100) NOT NULL,
    nm_fabricante  VARCHAR(100),
    nm_usuario  VARCHAR(100) NOT NULL,
    nm_ip_address  VARCHAR(15) NOT NULL,
    pw_password VARCHAR(255) NOT NULL,
    pw_enable VARCHAR(255) NOT NULL,      
    dt_device DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE  backup_tb(
    id_backup INT AUTO_INCREMENT PRIMARY   KEY,  
    device_id INT  NOT NULL,
    tx_backup TEXT,                      
    dt_backup DATETIME NOT  NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN  KEY  (device_id) REFERENCES   device_tb(id_device) ON DELETE CASCADE
);


CREATE TABLE config_tb(
    id_config INT AUTO_INCREMENT PRIMARY KEY,  
    device_id INT NOT NULL,
    sp_config TEXT,                      
    dt_config DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES device_tb(id_device) ON DELETE CASCADE
);


DESC config_tb;

