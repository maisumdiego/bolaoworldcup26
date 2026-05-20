---
title: Entidade: Usuários
date: 2026-05-15
tags:
  - database
  - models
aliases:
  - Participantes
  - Players
---

# 👤 Usuários (`dim_users`)

Gerencia o ciclo de vida dos participantes no sistema.

## 📄 Definição do Modelo
Cada usuário é uma instância de `User` (Flask-Login).

> [!info] Atributos Críticos
> - `is_approved`: Define se o usuário está ativo no ranking público.
> - `profile_pic`: URL ou nome do arquivo gerenciado via ==Cloudinary==.

## 🖇️ Conexões no Grafo
- **Cria** [[apostas|Palpites]].
- **Possui** estatísticas no [[score-engine|Ranking]].
- **Autentica-se** via [[auth|Sistema de Auth]].

---
[[index|« Voltar ao Início]]
