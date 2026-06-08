import argparse
import random
import socket
import time
from datetime import datetime

import protocol


def run_sensor(sensor_id, host, port, intervalo, base, variacao, total):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[{sensor_id}] conectado a {host}:{port}")
    buffer = bytearray()

    enviadas = 0
    try:
        while total is None or enviadas < total:
            temperatura = round(base + random.uniform(-variacao, variacao), 2)
            leitura = {
                "type": "reading",
                "sensor_id": sensor_id,
                "temperature": temperatura,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
            protocol.send_message(sock, leitura)

            resposta = protocol.recv_message(sock, buffer)
            if resposta is None:
                print(f"[{sensor_id}] servidor encerrou a conexão")
                break
            if resposta.get("type") == "ack":
                print(f"[{sensor_id}] enviado {temperatura}°C (ok)")
            else:
                print(f"[{sensor_id}] resposta inesperada: {resposta}")

            enviadas += 1
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print(f"\n[{sensor_id}] encerrando...")
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="Sensor de temperatura simulado")
    parser.add_argument("--id", required=True, help="identificador do sensor")
    parser.add_argument("--host", default="127.0.0.1", help="host do servidor")
    parser.add_argument("--port", type=int, default=5050, help="porta do servidor")
    parser.add_argument("--intervalo", type=float, default=2.0,
                        help="segundos entre leituras")
    parser.add_argument("--base", type=float, default=25.0,
                        help="temperatura base em °C")
    parser.add_argument("--variacao", type=float, default=3.0,
                        help="variação máxima (+/-) em °C")
    parser.add_argument("--total", type=int, default=None,
                        help="número de leituras (padrão: infinito)")
    args = parser.parse_args()

    run_sensor(args.id, args.host, args.port, args.intervalo,
               args.base, args.variacao, args.total)


if __name__ == "__main__":
    main()
