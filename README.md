# Monitoramento de Temperatura em Ambientes IoT

Projeto da disciplina CSC. É um sistema cliente-servidor feito em Python onde
sensores de temperatura mandam leituras para um servidor central. O servidor
guarda essas leituras e um painel de controle pode consultar a média de cada
sensor.

Integrantes: Clara Amazonas e Geovanna Soto.

## Arquivos

- `protocol.py`: funções para mandar e receber as mensagens (JSON sobre TCP).
- `server.py`: o servidor central. Abre uma thread para cada cliente, então
  consegue atender vários sensores ao mesmo tempo. Guarda as leituras na
  memória e calcula as médias quando o painel pede.
- `sensor_client.py`: simula um sensor mandando leituras de tempos em tempos.
- `painel_client.py`: o painel de controle, com um menu para fazer as consultas.

## O que precisa para rodar

Só Python 3.10 ou mais novo. Não usa nenhuma biblioteca de fora, só o que já
vem com o Python.

## Como rodar

Abra um terminal para cada parte, todos dentro da pasta do projeto.

Primeiro o servidor:

```bash
python server.py
```

Depois um ou mais sensores (cada um em um terminal):

```bash
python sensor_client.py --id sensor-01
python sensor_client.py --id sensor-02 --base 22 --variacao 4 --intervalo 3
```

Opções do sensor:

| Opção         | O que faz                                 | Padrão      |
|---------------|-------------------------------------------|-------------|
| `--id`        | Nome do sensor (obrigatório)              | —           |
| `--host`      | Host do servidor                          | `127.0.0.1` |
| `--port`      | Porta do servidor                         | `5050`      |
| `--intervalo` | Segundos entre cada leitura               | `2.0`       |
| `--base`      | Temperatura base em °C                    | `25.0`      |
| `--variacao`  | Variação máxima para mais ou menos em °C  | `3.0`       |
| `--total`     | Quantas leituras mandar (sem isso, manda sempre) | —    |

E por último o painel:

```bash
python painel_client.py
```

Ele mostra um menu:

```
=== Painel de Controle ===
1) Listar sensores
2) Média de um sensor
3) Média de todos os sensores
0) Sair
```

Para a opção 2 é preciso digitar o nome exato do sensor (o que foi passado em
`--id`, por exemplo `sensor-01`).

## As mensagens

Tudo que trafega entre cliente e servidor é JSON terminado por uma quebra de
linha. O sensor manda leituras assim:

```json
{"type": "reading", "sensor_id": "sensor-01", "temperature": 23.4,
 "timestamp": "2026-06-02T18:48:00"}
```

O painel pode pedir:

```json
{"type": "query_avg", "sensor_id": "sensor-01"}
{"type": "query_avg_all"}
{"type": "query_list"}
```

E o servidor responde com `ack` (confirmando uma leitura), `avg`, `avg_all`,
`list` ou `error`.

## Observações

- As leituras ficam só na memória, então se o servidor for reiniciado os dados
  somem.
- Para parar qualquer parte é só apertar Ctrl+C.
- A porta padrão é 5050. No macOS a porta 5000 costuma estar ocupada pelo
  AirPlay, por isso não usamos ela.
