from função.backup import conectar_dispositivo, fazer_backup
from função.devices import adicionar_device, escolher_device
from função.configuração import enviar_configuracao_ssh, gerenciar_configuracoes
from Banco_de_dados.db import conectar_banco


def main():
    db = conectar_banco()
    cursor = db.cursor(dictionary=True)

    while True:
        print("\n=== Menu Principal ===")
        print("1 - Adicionar novo dispositivo")
        print("2 - Conectar a um dispositivo")
        print("3 - Gerenciar configurações")
        print("4 - Sair")
        opcao = input("> ")

        if opcao == "1":
            adicionar_device(cursor, db)

        elif opcao == "2":
            device = escolher_device(cursor)
            if device:
                net_connect = conectar_dispositivo(device)
                if net_connect:
                    while True:
                        print(f"\n=== Ações para {device['nm_hostname']} ===")
                        print("1 - Fazer backup do dispositivo")
                        print("2 - Enviar comandos de configuração")
                        print("3 - Voltar ao menu principal")
                        acao = input("> ")

                        if acao == "1":
                            fazer_backup(net_connect, cursor, db, device)
                        elif acao == "2":
                            enviar_configuracao(net_connect, device, cursor, db)
                        elif acao == "3":
                            break
                        else:
                            print("❌ Ação inválida.")
                    net_connect.disconnect()

        elif opcao == "3":
            gerenciar_configuracoes(cursor, db)

        elif opcao == "4":
            print(" Saindo do sistema...")
            break

        else:
            print(" Opção inválida! Escolha novamente.")

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()