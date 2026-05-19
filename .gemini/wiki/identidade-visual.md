---
title: Identidade Visual
created_at: 2026-05-15
tags: [ui, branding]
---

# ?? Identidade Visual (Pulp Noir)

A est�tica \"Pulp Noir\" combina o submundo dos detetives retr� com a vibra��o arcade.

## ?? Paleta de Cores
- **Verde Noir:** `#0f172a` (Fundo) e `#064e3b` (Cards/Tabelas).
- **Ouro Pulp:** `#F59E0B` (Destaques, bot�es e bordas de foco).
- **Vermelho Igreja:** `#E11D48` (Sombras s�lidas de texto e alertas).

## ?? Tipografia Padr�o
- **T�tulos (H1, H2):** Fonte \"Bungee\", tamanho 3rem, text-shadow Vermelho Igreja.
- **Corpo e Nomes:** Fonte \"Montserrat\", pesos Bold (700) e Extra-Bold (900).

## ??? Componentes
- **Botões:** Devem usar a classe `.btn-salvar-pulp` com sombra sólida de 3px ou 6px.
- **Pódio:** Design flutuante com bordas coloridas no topo indicando a posição.
- **Imagens:** Imagens de branding (como logos) devem sofrer tratamento de cor via CSS filters para se adequarem à paleta Noir, evitando cores externas como azul ou verde limão.

## ?? Requisitos de Exportação de Imagem (Ranking)

Estes requisitos são imutáveis e devem ser seguidos rigorosamente para manter a fidelidade visual exigida:

1.  **Hierarquia Superior (Cima para Baixo):**
    *   Logo do Site (sempre com masking ou filtros para Ouro Pulp, seguindo o mesmo estilo visual do título 'RANKING GERAL').
    *   Título \"RANKING GERAL\" (fonte Bungee).
    *   Nome do Bolão \"Bolão da Cabeça 2026\".
2.  **Pódio Central:**
    *   Exibição dos 3 primeiros colocados na ordem visual 2º - 1º - 3º.
    *   Fidelidade ao design da página: selos numerados numerados (1, 2, 3), sem emojis.
3.  **Tabela de Classificação:**
    *   Deve conter as 7 posições subsequentes ao pódio (do 4º ao 10º lugar).
    *   **Remover cabeçalhos de coluna (POS, PARTICIPANTE, TOTAL).**
    *   **Exibir o sufixo "PTS" logo após o valor numérico dos pontos.**
    *   **Mesmo que não hajam usuários suficientes, deve-se inserir as colocações vazias como placeholders.**
    *   **O usuário logado deve sempre estar sendo mostrado e sinalizado (sinalizado exceto no pódio). Quando o usuário não estiver no top 10, ele deve ser colocado na décima posição, exibindo sua colocação real e a sinalização.**
    *   Destaque obrigatório para o usuário logado caso ele esteja nesta faixa.
4.  **Rodapé (Footer):**
    *   Remover URL ou nomes do torneio/copa.
    *   Exibir exclusivamente a **data e hora da geração da imagem**.
5.  **Estética Técnica:**
    *   Fidelidade absoluta ao visual da página de Ranking.
    *   Masking para a logo azul original.
    *   Layout robusto para evitar falhas no `dom-to-image` (evitar flexbox complexo e blur pesado).
