# 🔎 Análise de Transações Financeiras e Detecção de Anomalias/Fraudes

Projeto de portfólio que simula um cenário real do setor bancário: uma
base de transações de clientes é gerada de forma fictícia e, em seguida,
analisada em busca de **padrões suspeitos** que possam indicar fraude.

> ⚠️ Todos os dados usados aqui são **100% fictícios**, gerados
> aleatoriamente pelo próprio projeto. Nenhuma informação real de
> clientes ou bancos é utilizada.

---

## 🎯 Objetivo do projeto

Demonstrar, na prática, um fluxo comum em times de **dados / risco /
antifraude** de instituições financeiras:

1. Ter uma base de transações (aqui, gerada artificialmente).
2. Aplicar regras de negócio para detectar comportamentos incomuns.
3. Gerar um relatório de alertas para que um analista humano investigue.

As regras de detecção implementadas neste projeto são:

- **Valor alto em horário noturno** — transações acima de um valor
  limite (padrão: R$ 4.000) realizadas entre 00h e 06h.
- **Rajada de transações** — um mesmo cliente realizando 4 ou mais
  transações em um intervalo de até 10 minutos.

Essas duas regras são bastante usadas como primeiro filtro em sistemas
reais de antifraude, antes de modelos estatísticos/machine learning
mais complexos.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Uso no projeto |
|---|---|
| **Python 3** | Linguagem principal do projeto |
| **SQLite** | Banco de dados local (arquivo `.db`), simula um "SQL Server" de forma simples e sem precisar instalar nada |
| **SQL** | Consulta feita diretamente no banco (`SELECT ... FROM transacoes`) |
| **Pandas** | Manipulação dos dados, cálculo das janelas de tempo e geração dos alertas |

> 💡 O projeto usa **SQLite** (em vez de SQL Server) de propósito, pois
> ele não exige instalação de servidor — o banco inteiro é um único
> arquivo. Toda a lógica SQL usada (`CREATE TABLE`, `SELECT`,
> `INSERT`) é compatível com SQL Server com pouquíssimas adaptações,
> então isso não te impede de citar "SQL Server" no seu portfólio como
> tecnologia que você domina — só explique que localmente usou SQLite
> para facilitar a demonstração.

---

## 📁 Estrutura do projeto

```
├── gerar_dados.py          # Gera a base fictícia de transações (SQLite)
├── analise_fraudes.py      # Analisa os dados e gera os alertas
├── transacoes.db           # (criado ao rodar gerar_dados.py)
├── alertas_fraudes.csv     # (criado ao rodar analise_fraudes.py)
└── README.md