import os
import ipaddress
import datetime
from textwrap import dedent
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException


def validar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False


def validar_mask(mask):
    try:
        ipaddress.IPv4Network(f"10.0.0.0/{mask}", strict=False)
        return True
    except:
        return False


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

            data_hora = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M")

            config_dir = os.path.expanduser("~/Documentos/projetos/Python/PI/arquivos/conf")
            os.makedirs(config_dir, exist_ok=True)
            safe_hostname = device['nm_hostname'].replace(" ", "_")
            nm_back = os.path.join(config_dir, f"config_{safe_hostname}_{data_hora}.txt")

            with open(nm_back, "w") as f:
                f.write(output)

            print(f"\n Configuração enviada e salva em: {nm_back}")

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
        cursor.execute("SELECT * FROM device_tb")
        dispositivos = cursor.fetchall()

        print("\n=== Gerenciamento de Configurações ===")
        print("1 - Criar nova configuração completa")
        print("2 - Listar configurações existentes")
        print("3 - Deletar uma configuração")
        print("4 - Enviar configuração para o dispositivo")
        print("5 - Voltar ao menu principal")
        opcao = input("> ")

        if opcao == "1":
            print("\n=== Dispositivos disponíveis ===")
            for d in dispositivos:
                print(f"{d['id_device']} - {d['nm_hostname']} ({d['nm_ip_address']}) - {d['nm_fabricante']}")

            device_id = input("\n ID do dispositivo: ")

            print("\n Criação de usuário Admin:")
            hostname = input("Hostname: ")
            adm = input("Usuário admin: ")
            senha = input("Senha do usuário admin: ")
            enable = input("Senha ENABLE: ")

            print("\n!!! ATENÇÃO: ISSO PODE MUDAR O IP PERMANENTEMENTE !!!")
            dominio = input("Nome do domínio SSH: ")

            # ===== Validação de IP =====
            while True:
                ip_addr = input("Endereço IP (ex: 192.168.1.1): ")
                if validar_ip(ip_addr):
                    break
                print(" IP inválido. Tente novamente.\n")

            # ===== Validação de máscara =====
            while True:
                mask = input("Máscara (ex: 255.255.255.0): ")
                if validar_mask(mask):
                    break
                print(" Máscara inválida. Tente novamente.\n")

            # ===== Pergunta se é switch ou roteador =====
            tipo = input("\nO dispositivo é um switch? (s/n): ").lower()

            porta = ""
            vlan = ""

            # === SWITCH: perguntar VLAN ===
            if tipo == "s":
                while True:
                    vlan = input("Digite a VLAN de gerenciamento (ex: 1, 10, 20): ")

                    if vlan.isdigit() and 1 <= int(vlan) <= 4094:
                        break
                    print(" VLAN inválida! Digite um número entre 1 e 4094.\n")

            # === ROTEADOR: perguntar interface ===
            elif tipo == "n":
                porta = input("Interface física (ex: GigabitEthernet0/0): ").strip()

            else:
                print(" Opção inválida! Digite apenas 's' ou 'n'.")
                continue

            # ==== Geração da configuração ====
            comandos = dedent(f"""
            hostname {hostname}
            enable secret {enable}
            username {adm} privilege 15 secret {senha}
            ip domain-name {dominio}
            line vty 0 4
             login local
             transport input ssh
            exit
            """)

            # ===== SWITCH → VLAN escolhida =====
            if tipo == "s":
                comandos += dedent(f"""
                interface vlan {vlan}
                 ip address {ip_addr} {mask}
                 no shutdown
                exit
                """)

            # ===== ROTEADOR → Interface física =====
            elif tipo == "n":
                comandos += dedent(f"""
                interface {porta}
                 ip address {ip_addr} {mask}
                 no shutdown
                exit
                """)

            comandos += dedent("""
            end
            wr
            """)

            # Remove espaços extras
            comandos = "\n".join([linha.strip() for linha in comandos.splitlines() if linha.strip()])

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
            enviar_configuracao_ssh(cursor, db)

        elif opcao == "5":
            break

        else:
            print(" Opção inválida.")
            