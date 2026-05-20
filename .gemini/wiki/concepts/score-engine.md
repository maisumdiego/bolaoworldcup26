---
title: Motor de Pontuação
date: 2026-05-15
tags:
  - logic
  - backend
  - score
aliases:
  - Score Engine
  - Cálculo de Pontos
---

# ⚽ Motor de Pontuação

A inteligência de pontuação do Bolão é centralizada em `utils.py`.

> [!important] Integridade de Dados
> O cálculo é disparado apenas quando o status de um jogo é alterado para `encerrado`.

## 📊 Estrutura de Pontuação

| Tipo | Critério | Pontos | Tag |
| :--- | :--- | :---: | :--- |
| **Exato** | Acertou o placar exato de ambos os times. | **5** | `exato` |
| **Parcial** | Acertou o vencedor/empate + gols de um dos times. | **3** | `parcial` |
| **Tendência** | Acertou apenas o vencedor ou o empate. | **2** | `tendencia` |
| **Erro** | Errou completamente o resultado. | **0** | `erro` |

## 🏆 Critérios de Desempate
O ranking segue uma hierarquia rigorosa para evitar empates em excesso:
1. **Pontos Totais** (Soma acumulada)
2. **Placares Exatos** (Quem arrisca e acerta mais na mosca)
3. **Placares Parciais** (Consistência em placares aproximados)

## 🤖 Processamento Automatizado
- **Group Stage:** Atualiza `fact_group_standings` recursivamente.
- **Knockout Stage:** Promove o vencedor para o próximo `Game` usando o `placeholder_id` (ex: `W1` para o vencedor do Jogo 1).

> [!warning] Empate no Mata-mata
> Em caso de empate no tempo real, o sistema aguarda intervenção administrativa para definir quem avança (Pênaltis).

---
[[regras-de-negocio|« Voltar para Regras]]
