"""
analise_fraudes.py
--------------------
Script responsável por ANALISAR o banco de dados de transações
(gerado pelo script gerar_dados.py) e identificar possíveis
anomalias/fraudes, usando pandas + consultas SQL.

Regras de detecção implementadas:
    1. Transações de valor ALTO (acima de um limite definido) que
       ocorreram em horário NOTURNO (00h às 05h59).
    2. Clientes com MÚLTIPLAS transações em um curto intervalo de
       tempo (ex: 4 ou mais transações em até 10 minutos).

Ao final, o script:
    - Imprime os alertas encontrados no terminal.
    - Gera um resumo estatístico.
    - Exporta os alertas para um arquivo "alertas_fraudes.csv".

Como executar:
    python analise_fraudes.py

IMPORTANTE: rode primeiro o "gerar_dados.py" para criar o banco.
"""

import sqlite3
import pandas as pd

# ------------------------------------------------------------------
# 1. CONFIGURAÇÕES DA ANÁLISE (você pode alterar esses valores)
# ------------------------------------------------------------------

NOME_BANCO = "transacoes.db"

VALOR_LIMITE_NOTURNO = 4000        # acima disso, à noite, vira alerta
HORA_INICIO_NOTURNA = 0            # 00h
HORA_FIM_NOTURNA = 6               # até 05h59

JANELA_MINUTOS_RAJADA = 10         # intervalo considerado "curto"
QTD_MINIMA_RAJADA = 4              # a partir de quantas transações vira alerta

ARQUIVO_SAIDA_CSV = "alertas_fraudes.csv"


def carregar_dados():
    """Lê a tabela 'transacoes' do SQLite e devolve um DataFrame do pandas."""
    conexao = sqlite3.connect(NOME_BANCO)

    # Aqui usamos SQL "puro" dentro do pandas -> isso é o que a vaga/projeto
    # pede: uso conjunto de pandas + SQL.
    query = "SELECT * FROM transacoes ORDER BY id_cliente, data_hora"
    df = pd.read_sql_query(query, conexao)
    conexao.close()

    # Converte a coluna de texto para o tipo datetime do pandas,
    # isso facilita muito filtros por hora/dia depois.
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    return df


def detectar_valores_altos_noturnos(df):
    """
    Regra 1: transações com valor >= VALOR_LIMITE_NOTURNO que
    aconteceram entre HORA_INICIO_NOTURNA e HORA_FIM_NOTURNA.
    """
    hora = df["data_hora"].dt.hour

    filtro = (
        (df["valor"] >= VALOR_LIMITE_NOTURNO) &
        (hora >= HORA_INICIO_NOTURNA) &
        (hora < HORA_FIM_NOTURNA)
    )

    alertas = df[filtro].copy()
    alertas["tipo_alerta"] = "Valor alto em horário noturno"
    return alertas


def detectar_rajada_transacoes(df):
    """
    Regra 2: para cada cliente, verifica se existem QTD_MINIMA_RAJADA
    ou mais transações dentro de uma janela de JANELA_MINUTOS_RAJADA.

    Estratégia:
        - Para cada cliente, ordenamos as transações por data/hora.
        - Usamos uma "janela deslizante" baseada em tempo (rolling
          window) contando quantas transações caem dentro dos últimos
          X minutos a partir de cada transação.
    """
    lista_alertas = []

    for id_cliente, grupo in df.groupby("id_cliente"):
        grupo = grupo.sort_values("data_hora").set_index("data_hora")

        # rolling com janela de tempo: conta quantas transações existem
        # nos últimos JANELA_MINUTOS_RAJADA minutos, para cada linha.
        contagem = grupo["valor"].rolling(f"{JANELA_MINUTOS_RAJADA}min").count()

        indices_suspeitos = contagem[contagem >= QTD_MINIMA_RAJADA].index

        if len(indices_suspeitos) > 0:
            trechos = grupo.loc[indices_suspeitos].reset_index()
            trechos["id_cliente"] = id_cliente
            lista_alertas.append(trechos)

    if lista_alertas:
        alertas = pd.concat(lista_alertas, ignore_index=True)
    else:
        alertas = df.iloc[0:0].copy()  # DataFrame vazio com mesmas colunas

    alertas = alertas.copy()
    alertas["tipo_alerta"] = f"Múltiplas transações em até {JANELA_MINUTOS_RAJADA} min"

    # reordena colunas para ficar igual ao outro alerta
    colunas = ["id_transacao", "id_cliente", "data_hora", "valor",
               "tipo_transacao", "cidade", "tipo_alerta"]
    return alertas[colunas]


def gerar_resumo(df_total, alertas_valor_alto, alertas_rajada):
    """Imprime um resumo estatístico simples da análise."""
    total_transacoes = len(df_total)
    total_alertas_valor = len(alertas_valor_alto)
    total_alertas_rajada = alertas_rajada["id_transacao"].nunique()

    print("\n" + "=" * 55)
    print("RESUMO DA ANÁLISE DE FRAUDES")
    print("=" * 55)
    print(f"Total de transações analisadas .............. {total_transacoes}")
    print(f"Alertas - valor alto/noturno ................. {total_alertas_valor}")
    print(f"Alertas - rajada de transações ................ {total_alertas_rajada}")
    print(f"Total de clientes com pelo menos 1 alerta ..... "
          f"{pd.concat([alertas_valor_alto, alertas_rajada])['id_cliente'].nunique()}")
    print("=" * 55 + "\n")


def main():
    print("Carregando dados do banco...")
    df = carregar_dados()
    print(f"{len(df)} transações carregadas.\n")

    print("Analisando transações de valor alto em horário noturno...")
    alertas_valor_alto = detectar_valores_altos_noturnos(df)

    print("Analisando rajadas de transações por cliente...")
    alertas_rajada = detectar_rajada_transacoes(df)

    # Junta os dois tipos de alerta em uma única tabela final
    colunas_comuns = ["id_transacao", "id_cliente", "data_hora", "valor",
                       "tipo_transacao", "cidade", "tipo_alerta"]
    alertas_finais = pd.concat(
        [alertas_valor_alto[colunas_comuns], alertas_rajada[colunas_comuns]],
        ignore_index=True
    ).sort_values("data_hora")

    if alertas_finais.empty:
        print("\nNenhuma transação suspeita encontrada com as regras atuais.")
    else:
        print(f"\n{len(alertas_finais)} alertas encontrados. Exibindo os 15 primeiros:\n")
        print(alertas_finais.head(15).to_string(index=False))

    gerar_resumo(df, alertas_valor_alto, alertas_rajada)

    alertas_finais.to_csv(ARQUIVO_SAIDA_CSV, index=False)
    print(f"Arquivo '{ARQUIVO_SAIDA_CSV}' gerado com todos os alertas.")


if __name__ == "__main__":
    main()
