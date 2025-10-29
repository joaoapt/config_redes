from netmiko import ConnectHandler

def enviar_configuracao(net_connect, device):
    print("\nDigite os comandos de configuração (digite 'fim' para terminar):")
    commands = []
    while True:
        cmd = input("config> ")
        if cmd.lower() == "fim":
            break
        if cmd.strip():  # ignora linhas em branco
            commands.append(cmd)

    if not commands:
        print("Nenhum comando digitado. :(")
        return
    try:
        
        output = net_connect.send_config_set(commands)


        filename = f"config_{device['nm_hostname']}.log"
        with open(filename, "w") as f:
            f.write(output)


        net_connect.save_config()

        print(f"\n Configuração concluida com  SUCESSO!!!!!! Log salvo como: {filename}")
    except Exception as e:
        print(f":( Erro ao aplicar configuração: {e}")
