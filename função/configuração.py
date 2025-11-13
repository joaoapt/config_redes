import os
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

def enviar_configuracao_ssh(cursor, db):
    cursor.execute("SELECT * FROM device_tb")
    dispositivos = cursor.fetchall()

    if not dispositivos:
        print(" Nenhum dispositivo cadastrado no banco de dados.")
        return

    print("\n=== Dispositivos disponíveis ===")
    for d in dispositivos:
        print(f"{d['id_device']} - {d['nm_hostname']} ({d['nm_ip_address']}) - {d['nm_fabricante']}")

    try:
        device_id = int(input("\n Digite o ID do dispositivo para enviar a configuração: "))

        cursor.execute("SELECT * FROM device_tb WHERE id_device = %s", (device_id,))
        device = cursor.fetchone()

        if not device:
            print(" Dispositivo não encontrado.")
            return

        cursor.execute("""
            SELECT sp_config FROM config_tb 
            WHERE device_id = %s ORDER BY dt_config DESC LIMIT 1
        """, (device_id,))
        config = cursor.fetchone()

        if not config:
            print(" Nenhuma configuração encontrada para esse dispositivo.")
            return

        comandos = config['sp_config'].splitlines()
        print(f"\n Conectando ao dispositivo {device['nm_hostname']} ({device['nm_ip_address']})...")

        cisco = {
            "device_type": "cisco_ios",
            "host": device["nm_ip_address"],
            "username": device["nm_usuario"],
            "password": device["pw_password"],
            "secret": device["pw_enable"],
            "timeout": 60,
        }

        try:
            net_connect = ConnectHandler(**cisco)
            net_connect.enable()
            print(" Conexão SSH estabelecida. Enviando configuração...")

            output = net_connect.send_config_set(comandos)
            print(output)

        
            sql = "INSERT INTO backup_tb (device_id, tx_backup) VALUES (%s, %s)"
            cursor.execute(sql, (device_id, f"Config enviada:\n{output}"))
            db.commit()


            os.makedirs("config_log", exist_ok=True)
            safe_hostname = device["nm_hostname"].replace(" ", "_")
            filename = os.path.join("config_log", f"config_{safe_hostname}.txt")

            with open(filename, "w") as f:
                f.write(output)

            print(f"\n Configuração enviada e salva em: {filename}")

            net_connect.disconnect()

        except NetmikoTimeoutException:
            print(f" Timeout ao conectar em {device['nm_ip_address']}")
        except NetmikoAuthenticationException:
            print(f" Falha de autenticação em {device['nm_ip_address']}")
        except Exception as e:
            print(f" Erro ao enviar configuração: {e}")

    except ValueError:
        print(" ID inválido. Digite um número válido.")


def gerenciar_configuracoes(cursor, db):
    while True:
        print("\n=== Gerenciamento de Configurações ===")
        print("1 - Criar nova configuração completa")
        print("2 - Listar configurações existentes")
        print("3 - Deletar uma configuração")
        print("4 - Voltar ao menu principal")
        print("5 - Enviar configuração para o dispositivo")  
        opcao = input("> ")

        if opcao == "1":
            device_id = input("ID do dispositivo: ")

            print("\n Vamos montar a configuração do roteador:")
            hostname = input("Hostname do roteador: ")
            usuario = input("Usuário admin: ")
            senha_usuario = input("Senha do usuário admin: ")
            senha_enable = input("Senha ENABLE: ")
            ip_int = input("Interface (ex: GigabitEthernet0/0): ")
            ip_addr = input("Endereço IP (ex: 192.168.1.1): ")
            mask = input("Máscara (ex: 255.255.255.0): ")

            comandos = f"""hostname {hostname}
            enable secret {senha_enable}
            username {usuario} privilege 15 secret {senha_usuario}
            line vty 0 4
            login local
            transport input ssh
            interface {ip_int}
            ip address {ip_addr} {mask}
            no shutdown
            end
            wr
            """

            print("\nConfiguração gerada:\n")
            print(comandos)
            confirmar = input("Deseja salvar essa configuração? (s/n): ").lower()
            if confirmar != "s":
                print(" Configuração cancelada.")
                continue

            sql = "INSERT INTO config_tb (device_id, sp_config) VALUES (%s, %s)"
            cursor.execute(sql, (device_id, comandos))
            db.commit()
            print(" Configuração salva com sucesso!")

        elif opcao == "2":
            cursor.execute("""
                SELECT c.id_config, d.nm_hostname, c.dt_config
                FROM config_tb c
                JOIN device_tb d ON c.device_id = d.id_device
                ORDER BY c.dt_config DESC
            """)
            configs = cursor.fetchall()

            if not configs:
                print(" Nenhuma configuração encontrada.")
            else:
                print("\n Configurações registradas:")
                for cfg in configs:
                    print(f"{cfg['id_config']} - {cfg['nm_hostname']} ({cfg['dt_config']})")

        elif opcao == "3":
            config_id = input("Digite o ID da configuração que deseja excluir: ")
            cursor.execute("DELETE FROM config_tb WHERE id_config = %s", (config_id,))
            db.commit()
            print(" Configuração removida com sucesso!")

        elif opcao == "4":
            break

        elif opcao == "5":
            enviar_configuracao_ssh(cursor, db)  

        else:
            print(" Opção inválida.")
