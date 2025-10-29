from  função.backup import conectar_dispositivo, fazer_backup
from Banco_de_dados.db import conectar_banco
from função.devices import adicionar_device, escolher_device


def main():
    db = conectar_banco() 
    cursor = db.cursor(dictionary=True)

    while True:
        print("\n=== Menu Principal ===")
        print("1 - Adicionar novo dispositivo")
        print("2 - Conectar a um dispositivo")
        print("3 - Sair")
        opcao = input("> ")

        if opcao == "1":
            adicionar_device(cursor, db)
        elif opcao == "2":
            device = escolher_device(cursor)
            if device:
                net_connect = conectar_dispositivo(device)
                if net_connect:
                    print("\nEscolha uma ação:")
                    print("1 - Fazer backup")
                    print("2 - Enviar comandos de configuração")
                    acao = input("> ")
                    if acao == "1":
                        fazer_backup(net_connect, cursor, db, device)
                    elif acao == "2":
                        print("esse não !!!")
                        enviar_configuracao(net_connect, device)
                    else:
                        print("❌ Ação inválida")
                    net_connect.disconnect()
        elif opcao == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()