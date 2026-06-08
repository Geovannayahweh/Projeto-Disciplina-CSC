import argparse
import socket

import protocol


MENU = """
=== Painel de Controle ===
1) Listar sensores
2) Média de um sensor
3) Média de todos os sensores
0) Sair
Escolha: """


def listar(sock, buffer):
    protocol.send_message(sock, {"type": "query_list"})
    resp = protocol.recv_message(sock, buffer)
    sensores = resp.get("sensors", [])
    if sensores:
        print("Sensores registrados:")
        for s in sensores:
            print(f"  - {s}")
    else:
        print("Nenhum sensor registrou dados ainda.")


def media_sensor(sock, buffer):
    sensor_id = input("ID do sensor: ").strip()
    protocol.send_message(sock, {"type": "query_avg", "sensor_id": sensor_id})
    resp = protocol.recv_message(sock, buffer)
    if resp.get("type") == "avg":
        print(f"Média de {resp['sensor_id']}: {resp['average']}°C "
              f"({resp['count']} leituras)")
    else:
        print(f"Erro: {resp.get('message')}")


def media_todos(sock, buffer):
    protocol.send_message(sock, {"type": "query_avg_all"})
    resp = protocol.recv_message(sock, buffer)
    averages = resp.get("averages", {})
    if averages:
        print("Médias por sensor:")
        for sensor_id, info in sorted(averages.items()):
            print(f"  {sensor_id}: {round(info['average'], 2)}°C "
                  f"({info['count']} leituras)")
    else:
        print("Nenhum dado disponível.")


def main():
    parser = argparse.ArgumentParser(description="Painel de controle de temperatura")
    parser.add_argument("--host", default="127.0.0.1", help="host do servidor")
    parser.add_argument("--port", type=int, default=5050, help="porta do servidor")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))
    print(f"[painel] conectado a {args.host}:{args.port}")
    buffer = bytearray()

    try:
        while True:
            escolha = input(MENU).strip()
            if escolha == "1":
                listar(sock, buffer)
            elif escolha == "2":
                media_sensor(sock, buffer)
            elif escolha == "3":
                media_todos(sock, buffer)
            elif escolha == "0":
                break
            else:
                print("Opção inválida.")
    except (KeyboardInterrupt, EOFError):
        print("\n[painel] encerrando...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
