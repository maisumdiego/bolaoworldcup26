---
title: Estilo Pulp Noir
date: 2026-05-15
tags:
  - ui
  - css
  - branding
aliases:
  - Pulp Style
  - Identidade Visual Detalhada
---

# 🎨 Estilo Pulp Noir

O **Pulp Noir** é a gramática visual exclusiva do projeto. Ele funde a rusticidade de revistas pulp com a sofisticação sombria do estilo Noir.

> [!tip] Regra de Ouro da UI
> Cada elemento deve parecer "físico" e ter peso. Use sombras sólidas e contrastes vibrantes em fundos profundos.

## 🌈 Paleta de Cores (Tokens)
- **Fundo (Void):** `#0f172a` — ==Azul Marinho Profundo==.
- **Cards (Slate):** `#1e293b` — Usado em superfícies secundárias.
- **Acento (Gold):** `#F59E0B` — O "Ouro Pulp" para destaques e CTAs.
- **Alerta (Church Red):** `#E11D48` — Vermelho para erros e sombras de destaque.

## 🧱 Componentes de Assinatura

### Botões Pulp (`.btn-pulp-jump`)
Possuem um efeito de profundidade simulado por sombras sólidas.
> [!info] Comportamento
> No hover, o botão "salta" (`translateY(-5px)`) e a sombra aumenta para `6px`. No clique, ele retorna ao estado base.

### Inputs de Placar
- ==Fundo Ultra-escuro== (`#020617`).
- Fonte ==Bungee== para os números.
- Efeito de escala ao ganhar foco.

## 📱 Responsividade (Pódio)
No desktop, o 1º lugar é centralizado (`order: 2`). No mobile, a estrutura é linear e vertical:
1. [[#Pódio 1º Lugar]]
2. [[#Pódio 2º Lugar]]
3. [[#Pódio 3º Lugar]]

---
[[identidade-visual|« Voltar para Identidade Visual]]
