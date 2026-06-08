import argparse
import socket
import threading
from collections import defaultdict
from datetime import datetime

import protocol


class TemperatureStore:
    def __init__(self):
        self._readings = defaultdict(list)
        self._lock = threading.Lock()

    def add_reading(self, sensor_id: str, temperature: float, timestamp: str):
        with self._lock:
            self._readings[sensor_id].append(
                {"temperature": temperature, "timestamp": timestamp}
            )

    def average(self, sensor_id: str):
        with self._lock:
            readings = self._readings.get(sensor_id, [])
            if not readings:
                return None, 0
            temps = [r["temperature"] for r in readings]
            return sum(temps) / len(temps), len(temps)

    def average_all(self) -> dict:
        with self._lock:
            result = {}
            for sensor_id, readings in self._readings.items():
                temps = [r["temperature"] for r in readings]
                result[sensor_id] = {
                    "average": sum(temps) / len(temps),
                    "count": len(temps),
                }
            return result

    def sensors(self) -> list:
        with self._lock:
            return sorted(self._readings.keys())


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.store = TemperatureStore()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen()
        print(f"[servidor] escutando em {self.host}:{self.port}")

        try:
            while True:
                client_sock, addr = server_sock.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_sock, addr),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[servidor] encerrando...")
        finally:
            server_sock.close()

    def handle_client(self, client_sock: socket.socket, addr):
        print(f"[servidor] conexão de {addr}")
        buffer = bytearray()
        try:
            while True:
                message = protocol.recv_message(client_sock, buffer)
                if message is None:
                    break
                response = self.process(message, addr)
                if response is not None:
                    protocol.send_message(client_sock, response)
        except (ConnectionError, ValueError) as exc:
            print(f"[servidor] erro com {addr}: {exc}")
        finally:
            client_sock.close()
            print(f"[servidor] conexão encerrada {addr}")

    def process(self, message: dict, addr) -> dict | None:
        msg_type = message.get("type")

        if msg_type == "reading":
            sensor_id = message.get("sensor_id")
            temperature = message.get("temperature")
            timestamp = message.get("timestamp") or datetime.now().isoformat()
            if sensor_id is None or temperature is None:
                return {"type": "error", "message": "leitura incompleta"}
            self.store.add_reading(sensor_id, float(temperature), timestamp)
            print(f"[leitura] {sensor_id}: {temperature}°C @ {timestamp}")
            return {"type": "ack"}

        if msg_type == "query_avg":
            sensor_id = message.get("sensor_id")
            avg, count = self.store.average(sensor_id)
            if avg is None:
                return {
                    "type": "error",
                    "message": f"sem dados para o sensor '{sensor_id}'",
                }
            return {
                "type": "avg",
                "sensor_id": sensor_id,
                "average": round(avg, 2),
                "count": count,
            }

        if msg_type == "query_avg_all":
            return {"type": "avg_all", "averages": self.store.average_all()}

        if msg_type == "query_list":
            return {"type": "list", "sensors": self.store.sensors()}

        return {"type": "error", "message": f"tipo desconhecido: {msg_type}"}


def main():
    parser = argparse.ArgumentParser(description="Servidor de temperatura IoT")
    parser.add_argument("--host", default="0.0.0.0", help="endereço de bind")
    parser.add_argument("--port", type=int, default=5050, help="porta TCP")
    args = parser.parse_args()

    Server(args.host, args.port).start()


if __name__ == "__main__":
    main()
