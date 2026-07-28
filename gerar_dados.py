"""
gerar_dados.py
----------------
Script responsável por gerar uma base de dados FICTÍCIA de transações
bancárias, salva em um banco SQLite local (arquivo transacoes.db).

Objetivo didático: simular um cenário real onde temos milhares de
transações de clientes, algumas normais e outras "suspeitas" (inseridas
de propósito), para depois serem analisadas pelo script
analise_fraudes.py.

Como executar:
    python gerar_dados.py

Isso vai criar o arquivo "transacoes.db" na mesma pasta.
"""

import sqlite3
import random
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# 1. CONFIGURAÇÕES GERAIS
# ------------------------------------------------------------------

NOME_BANCO = "transacoes.db"          # nome do arquivo do banco SQLite
QTD_CLIENTES = 40                     # quantos clientes fictícios existirão
QTD_TRANSACOES_NORMAIS = 1500         # quantidade de transações "normais"
QTD_TRANSACOES_SUSPEITAS = 60         # quantidade de transações inseridas de propósito como suspeitas

# Data inicial da simulação (últimos 30 dias a partir de hoje)
DATA_FIM = datetime.now()
DATA_INICIO = DATA_FIM - timedelta(days=30)

CIDADES = [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba",
    "Porto Alegre", "Salvador", "Recife", "Brasília", "Fortaleza", "Manaus"
]

TIPOS_TRANSACAO = ["PIX", "TED", "DOC", "Saque", "Compra Cartão", "Transferência Interna"]


def criar_banco():
    """Cria (ou recria) o banco de dados e a tabela 'transacoes'."""
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()

    # Apaga a tabela se já existir, para podermos rodar o script várias vezes
    cursor.execute("DROP TABLE IF EXISTS transacoes")

    cursor.execute("""
        CREATE TABLE transacoes (
            id_transacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo_transacao TEXT NOT NULL,
            cidade TEXT NOT NULL
        )
    """)

    conexao.commit()
    return conexao


def gerar_data_hora_aleatoria():
    """Gera uma data/hora aleatória dentro do período simulado (30 dias)."""
    delta_segundos = int((DATA_FIM - DATA_INICIO).total_seconds())
    segundos_aleatorios = random.randint(0, delta_segundos)
    return DATA_INICIO + timedelta(seconds=segundos_aleatorios)


def gerar_transacoes_normais(conexao):
    """
    Gera transações consideradas "normais": valores baixos/médios,
    distribuídas em qualquer horário do dia.
    """
    cursor = conexao.cursor()
    registros = []

    for _ in range(QTD_TRANSACOES_NORMAIS):
        id_cliente = random.randint(1, QTD_CLIENTES)
        data_hora = gerar_data_hora_aleatoria()
        valor = round(random.uniform(10, 3000), 2)
        tipo = random.choice(TIPOS_TRANSACAO)
        cidade = random.choice(CIDADES)

        registros.append((id_cliente, data_hora.strftime("%Y-%m-%d %H:%M:%S"), valor, tipo, cidade))

    cursor.executemany("""
        INSERT INTO transacoes (id_cliente, data_hora, valor, tipo_transacao, cidade)
        VALUES (?, ?, ?, ?, ?)
    """, registros)

    conexao.commit()
    print(f"[OK] {QTD_TRANSACOES_NORMAIS} transações normais geradas.")


def gerar_transacoes_suspeitas(conexao):
    """
    Gera transações propositalmente SUSPEITAS, para que o script de
    análise consiga encontrá-las depois. Dois padrões são simulados:

    a) Transações de valor ALTO em horário NOTURNO (entre 00h e 05h).
    b) Várias transações em sequência rápida (poucos minutos) para o
       mesmo cliente - simulando um possível golpe ou uso indevido do cartão.
    """
    cursor = conexao.cursor()
    registros = []

    metade = QTD_TRANSACOES_SUSPEITAS // 2

    # a) Valores altos em horário noturno
    for _ in range(metade):
        id_cliente = random.randint(1, QTD_CLIENTES)
        dia_aleatorio = DATA_INICIO + timedelta(days=random.randint(0, 29))
        hora_noturna = random.randint(0, 5)  # 00h às 05h59
        minuto = random.randint(0, 59)
        data_hora = dia_aleatorio.replace(hour=hora_noturna, minute=minuto, second=0)

        valor = round(random.uniform(5000, 20000), 2)  # valor bem acima do padrão
        tipo = random.choice(["PIX", "TED", "Saque"])
        cidade = random.choice(CIDADES)

        registros.append((id_cliente, data_hora.strftime("%Y-%m-%d %H:%M:%S"), valor, tipo, cidade))

    # b) Rajada de transações em curto intervalo para o mesmo cliente
    qtd_rajadas = metade // 4 if metade >= 4 else 1
    for _ in range(qtd_rajadas):
        id_cliente = random.randint(1, QTD_CLIENTES)
        inicio_rajada = gerar_data_hora_aleatoria()

        # gera de 4 a 6 transações em sequência, com poucos minutos de diferença
        qtd_nesta_rajada = random.randint(4, 6)
        for i in range(qtd_nesta_rajada):
            data_hora = inicio_rajada + timedelta(minutes=random.randint(1, 3) * i)
            valor = round(random.uniform(200, 1500), 2)
            tipo = random.choice(["Compra Cartão", "PIX"])
            cidade = random.choice(CIDADES)
            registros.append((id_cliente, data_hora.strftime("%Y-%m-%d %H:%M:%S"), valor, tipo, cidade))

    cursor.executemany("""
        INSERT INTO transacoes (id_cliente, data_hora, valor, tipo_transacao, cidade)
        VALUES (?, ?, ?, ?, ?)
    """, registros)

    conexao.commit()
    print(f"[OK] {len(registros)} transações suspeitas geradas (inseridas de propósito).")


def main():
    print("Gerando base de dados fictícia de transações bancárias...\n")
    conexao = criar_banco()
    gerar_transacoes_normais(conexao)
    gerar_transacoes_suspeitas(conexao)

    total = conexao.execute("SELECT COUNT(*) FROM transacoes").fetchone()[0]
    conexao.close()

    print(f"\nBanco de dados '{NOME_BANCO}' criado com sucesso!")
    print(f"Total de transações geradas: {total}")
    print("Agora você pode rodar: python analise_fraudes.py")


if __name__ == "__main__":
    main()
