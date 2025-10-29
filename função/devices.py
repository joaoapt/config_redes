def adicionar_device(cursor, db):
    
    print(f"\n=== Adicionar novo dispositivo ===")
    hostname = input(f"Hostname: ") # nome enchergado na rede;
    fabricante = input(f"nome do fabricante: ") 
    ip = input(f"IP do dispositivo: ") 
    usuario = input(f"nome do usuario: ") # Usuario com acesso ao adiministrador do equipamento 
    password = input(f"Senha: ")
    enable = input(f"Senha Enable: ")
   
    sql = """
    INSERT INTO device_tb (nm_hostname, nm_fabricante, nm_usuario, nm_ip_address, pw_password, pw_enable)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (hostname, fabricante, usuario, ip, password, enable))
    db.commit()
    print(f"Dispositivo {hostname} adicionado com SUCESSO!!!! \n")


def listar_dispositivos(cursor):
    cursor.execute("SELECT * FROM device_tb")
    devices = cursor.fetchall()
    if not devices:
        print(f"Nenhum dispositivo cadastrado. :(")
        return []

    print(f"\n=== Dispositivos disponíveis ===")
    for d in devices:
        print(f"{d['id_device']} - {d['nm_hostname']} ({d['nm_ip_address']}) {d['dt_device']}")
    return devices


def escolher_device(cursor):
    devices = listar_dispositivos(cursor)
    if not devices:
        return None

    device_id = int(input(f"Escolha o ID do dispositivo: "))
    cursor.execute("SELECT * FROM device_tb WHERE id_device = %s", (device_id,))
    return cursor.fetchone()