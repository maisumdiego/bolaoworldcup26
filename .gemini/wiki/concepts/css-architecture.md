---
title: Arquitetura CSS (Pulp Noir)
tags: [css, architecture, pulp-noir]
---

# 🏗️ Arquitetura CSS (Pulp Noir)

O projeto utiliza uma abordagem baseada em **Componentes Core Unificados** com prefixo .pulp-. Esta arquitetura visa centralizar a gramática visual e facilitar a manutenção, eliminando estilos duplicados nos templates.

## 💎 Design Tokens (:root)

As variáveis globais definem a base de toda a interface:

- **Cores:**
  - --pulp-void: Fundo principal (#0f172a).
  - --pulp-gold: Destaque e interatividade (#F59E0B).
  - --pulp-red: Acentos e alertas (#E11D48).
- **Sombras (Pulp Shadow):**
  - --pulp-shadow-sm: Sombra sólida de 3px.
  - --pulp-shadow-md: Sombra sólida de 6px.
- **Radii:**
  - --pulp-radius-md: 12px para cards.
  - --pulp-radius-lg: 50px para pílulas e botões circulares.

## 🧱 Componentes Principais

### [[pulp-btn|Botões (.pulp-btn)]]
Substituem todas as variações anteriores (.btn-salvar-pulp, .dia-btn, etc.).
- **Modificadores:** --gold, --red, --outline, --jump.

### [[pulp-card|Cards (.pulp-card)]]
Base para todos os elementos de conteúdo (Jogos, Regras, Times).
- **Efeito:** Gradiente sutil + borda dourada interativa.

### [[pulp-nav|Navegação Interna (.pulp-nav)]]
Padronização de menus horizontais em estilo pílula com scroll horizontal automático.

---
[[identidade-visual|Voltar para Identidade Visual]]
