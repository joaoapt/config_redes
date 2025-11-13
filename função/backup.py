import os
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

def conectar_dispositivo(device):
    try:
        print(f"\n Conectando ao dispositivo {device['nm_hostname']} ({device['nm_ip_address']})...")

        cisco = {
            "device_type": "cisco_ios",
            "host": device["nm_ip_address"],
            "username": device["nm_usuario"],
            "password": device["pw_password"],
             "secret": device["pw_enable"],
            "timeout": 60,
        }

        net_connect = ConnectHandler(**cisco)
        net_connect.enable()
        if cisco["secret"]:
            net_connect.enable()

        print(f" Conexão SSH estabelecida com {device['nm_hostname']}!\n")
        return net_connect

    except NetmikoTimeoutException:
        print(f" Timeout ao conectar em {device['nm_ip_address']}")
    except NetmikoAuthenticationException:
        print(f" Falha de autenticação em {device['nm_ip_address']}.")
    except Exception as e:
        print(f" Erro inesperado: {e}")

    return None


def fazer_backup(net_connect, cursor, db, device):
    try:
        print(f"\n Iniciando backup do dispositivo {device['nm_hostname']}...")

        
        net_connect.send_command("terminal length 0")

        output = net_connect.send_command("show running-config")

        sql = "INSERT INTO backup_tb (device_id, tx_backup) VALUES (%s, %s)"
        cursor.execute(sql, (device["id_device"], output))
        db.commit()

        backup_dir = "backup"
        os.makedirs(backup_dir, exist_ok=True)

        
        safe_hostname = device['nm_hostname'].replace(" ", "_")
        filename = os.path.join(backup_dir, f"backup_{safe_hostname}.txt")

        # Salvar 
        with open(filename, "w") as f:
            f.write(output)


        print(f" Backup concluído com sucesso!")
        print(f"Arquivo salvo como: {filename}\n")

    except Exception as e:
        print(f" Erro ao realizar backup: {e}")
