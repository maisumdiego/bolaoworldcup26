---
title: Log de Erros e Estabilização do Ranking
tags: [log, debugging, share]
---

# 📝 Log de Erros: Sistema de Compartilhamento do Ranking

Este documento registra as falhas cometidas durante a implementação da exportação de imagem para evitar reincidências e garantir a estabilidade do código.

## 🔴 Erros Identificados e Protocolos de Prevenção

### 1. Conflito de Sintaxe Jinja2 vs JavaScript (`startsWith`)
- **Erro:** Substituição global de `.startswith` (Python) por `.startsWith` (JS) dentro de tags do servidor `{% %}`.
- **Consequência:** `Jinja2 UndefinedError`, a página sequer carregava no servidor.
- **Protocolo:** Nunca usar "Replace All" em arquivos `.html`. Diferenciar cirurgicamente o que é lógica de template (Python) e o que é script (Browser).

### 2. Injeção de JSON Insegura (Aspas Simples)
- **Erro:** Uso de `JSON.parse('{{ data|tojson }}')` com aspas simples envolvendo o objeto.
- **Consequência:** Nomes de usuários com apóstrofos (ex: "D'Artagnan") quebravam a string do JS, causando erro de sintaxe e travando todos os botões da página.
- **Protocolo:** Usar injeção direta: `const data = {{ data|tojson|safe }};`.

### 3. Congelamento do `dom-to-image` (Flexbox + Imagens)
- **Erro:** Uso de `display: flex` em containers de imagem dentro da zona de captura.
- **Consequência:** A biblioteca `dom-to-image` travava silenciosamente ao renderizar o canvas, deixando o botão no estado "PROCESSANDO..." para sempre.
- **Protocolo:** Usar layouts de tabela (`display: table`) ou blocos simples (`display: block`) com margens para alinhamento na zona de captura. Evitar Flexbox aninhado complexo em elementos que serão convertidos em imagem.

### 4. Dependência de API de Fontes (`document.fonts.ready`)
- **Erro:** Envolver o processo de captura em `document.fonts.ready`.
- **Consequência:** Em alguns navegadores ou condições de cache, a promessa nunca resolvia, impedindo o disparo do download.
- **Protocolo:** Remover o wrapper de fontes ou usar um `setTimeout` de segurança. Priorizar a execução direta com delay controlado.

### 5. Sintaxe JS Mista (`startswith` vs `startsWith`)
- **Erro:** Uso acidental de `.startswith()` (Python) em blocos de código JavaScript.
- **Consequência:** `TypeError: user.profile_pic.startswith is not a function`.
- **Protocolo:** Revisar rigorosamente a capitalização em JS (`camelCase`).

---
**Status Atual:** Em fase de estabilização final. Próximo passo: Simplificação total do script para eliminação de qualquer ponto de falha latente.
