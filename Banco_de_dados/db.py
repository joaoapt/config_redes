import mariadb


def conectar_banco():
    try:
        Ban = mariadb.connect(
            host="127.0.0.1",
            user="joao",
            password="1234arch",
            database="redes_db"
        )
        print("Banco de Dados está funcionando com SUCESSO!!!!")
        return Ban
    except mariadb.Error as e:
        print(f"Erro ao conectar: {e} :(")
        exit()




# dml Device

def cadastro_device(hostname, fabricante, usuario, ip, password, enable):
    now = datetime.now()
    cursor.execute(
        "INSERT INTO device_tb (nm_hostname, nm_fabricante, nm_usurio, nm_ip_address, pw_password, pw_enable) VALUES (?, ?, ?, ?, ?, ?)",
        (hostname, fabricante, usuario, ip, password, enable)
    )
    Ban.commit()
    print(f"Dispositivo '{hostname}' adicionado com SUCESSO!!!!!!!")

def busca_device():
    cursor.execute("SELECT * FROM device_tb")
    return cursor.fetchall()

def remove_device(device_id):
    cursor.execute("DELETE FROM device_tb WHERE id_device=?", (device_id,))
    Ban.commit()
    print(f"Dispositivo {device_id} removido com SUCESSO!!!!!!!!")


# dml Backup

def cadastrado_backup(device_id, backup_data):
    now = datetime.now()
    cursor.execute(
        "INSERT INTO backup_tb (device_id, sp_backup) VALUES (?, ?)",
        (device_id, backup_data)
    )
    Ban.commit()
    print(f"Backup {device_id} adicionado com SUCESSO!!!!!!!!")

def busca_backups():
    cursor.execute("SELECT * FROM backup_tb")
    return cursor.fetchall()


# dml Config

def cadastrado_config(device_id, config_data):
    now = datetime.now()
    cursor.execute(
        "INSERT INTO config_tb (device_id, sp_config) VALUES (?, ?)",
        (device_id, config_data)
    )
    Ban.commit()
    print(f"Config para device {device_id} adicionado com SUCESSO!!!!!!!.")

def busca_configs():
    cursor.execute("SELECT * FROM config_tb")
    return cursor.fetchall()