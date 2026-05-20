---
title: Entidade: Jogos e Times
created_at: 2026-05-15
tags: [models, football, database]
---

# 🏟️ Jogos e Times

## 🛡️ Times (`dim_teams`)
Armazena as seleções nacionais.
- `ab`: Sigla de 3 letras (ex: BRA, ARG).
- `group_team`: Letra do grupo (A-L).
- `fifa_ranking`: Usado para curiosidades e informações de contexto.

## 🎮 Jogos (`dim_games`)
A espinha dorsal do torneio.
- `phase`: Grupos, Oitavas, Quartas, Semifinal, Final.
- `status`: `agendado`, `encerrado`.
- `placeholder_a/b`: Utilizado para o chaveamento automático (ex: `1A`, `W73`).

## 📈 Classificação (`fact_group_standings`)
Tabela dinâmica que calcula vitórias, empates, derrotas e saldo de gols em tempo real.

---
[[index|Voltar para o Índice]]
