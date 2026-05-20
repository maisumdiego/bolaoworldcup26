---
title: Histórico de Mudanças (Passo a Passo)
tags: [log, dev, refatoracao]
---

# ?? Histórico de Mudanças

Este documento registra as alterações feitas no projeto a partir de 19 de maio de 2026, visando estabilidade e consistência visual.

## [2026-05-19] - Passo 1: Lógica do Ranking
- **Arquivo:** \outes/main.py\
- **Mudança:** Implementada ordenação robusta por Pontos -> Exatos -> Parciais -> Tendência -> Nome.
- **Motivo:** Garantir que o critério primário seja sempre o total de pontos.

## [2026-05-19] - Passo 2: Arquitetura de Botões (Core)
- **Arquivo:** \static/css/style.css\
- **Mudança:** Criadas as classes \.pulp-btn\, \.pulp-btn-gold\ e \.pulp-btn-blue\.
- **Motivo:** Padronizar todos os botões do site com a sombra sólida e o efeito 'Jump' (baseado no botão de palpites original).


## [2026-05-19] - Passo 3: Limpeza da Home e Padronização de Botões
- **Arquivo:** \	emplates/index.html\
- **Mudança:** Aplicada a classe \.pulp-btn-gold\ no botão principal e removidos estilos inline redundantes.
- **Motivo:** Unificação visual e facilitação da manutenção futura.


## [2026-05-19] - Passo 4: Novo Padrão de Botão Luminoso (Glow)
- **Arquivo:** \static/css/style.css\
- **Mudança:** A classe \.pulp-btn\ foi redesenhada. Substituído o efeito de salto e sombra sólida por um efeito luminoso (glow) ao passar o mouse, inspirado no seletor de datas. Tamanho e fonte aumentados em 30%.
- **Motivo:** Pedido direto do usuário para alinhar os CTAs (Home e Ranking) com o padrão visual luminoso da página de Palpites.


## [2026-05-19] - Passo 5: Refino Estético da Home e Modal Raio-X
- **Arquivo:** \static/css/style.css\, \	emplates/index.html\
- **Mudanças:** 
  1. Botão \.pulp-btn\ ajustado para sombra sólida de 2px (estilo seletor de datas).
  2. Removida sombra vermelha no hover dos cards de pontuação.
  3. Logo do banner aumentada para 100px (desktop) e otimizada para 60px (mobile).
  4. Modal Raio-X restaurado com estética Pulp Noir (fundo escuro, bordas douradas, Intelligence Data). Título do bloco Wikipedia alterado para 'Sobre o país'.
- **Motivo:** Alinhamento com as preferências de design do usuário e melhoria da responsividade.


## [2026-05-19] - Passo 5.1: Correção Crítica do Raio-X e Refino da Logo
- **Arquivo:** \	emplates/index.html\
- **Mudanças:** 
  1. Corrigida a lógica JavaScript do Raio-X que apresentava erro de 'Inteligência não encontrada' devido a variáveis indefinidas.
  2. Logo do banner centralizada e redimensionada (420px desktop / 180px mobile) para evitar deslocamentos indesejados.
  3. Sombra do botão e dos cards ajustada conforme feedback (sombra sólida de 2px no botão, sombra preta nos cards).


## [2026-05-19] - Passo 5.2: Correção de Proporções e Tipografia do Raio-X
- **Arquivos:** \static/css/style.css\, \	emplates/index.html\
- **Mudanças:** 
  1. Restaurada a logo da navbar para 70px (tamanho original aprovado).
  2. Logo do banner aumentada para 450px (desktop) e 220px (mobile) com centralização forçada.
  3. Adicionada hifenização automática (\hyphens: auto\) e quebra de palavra (\word-break\) no texto 'Sobre o País' do Raio-X.


## [2026-05-19] - Passo 5.3: Expansão do Hero Banner Mobile
- **Arquivo:** \	emplates/index.html\
- **Mudanças:** 
  1. Hero Banner expandido para ocupar quase toda a primeira dobra no mobile (\min-height: 85vh\).
  2. Logo do banner no mobile aumentada para 320px (era 220px).
  3. Padding vertical no mobile aumentado para 6rem para melhor distribuição dos elementos.
  4. Ajuste na sombra projetada da logo para garantir centralização perfeita.


## [2026-05-19] - Passo 5.5: Refino de Arredondamento (Estilo Pílula)
- **Arquivo:** \static/css/style.css\
- **Mudança:** Border-radius da classe \.pulp-btn\ aumentado para 50px.
- **Motivo:** Pedido do usuário para arredondar mais o botão principal (estilo pílula).


## [2026-05-19] - Passo 5.6: Padronização dos Botões de Login/Cadastro
- **Arquivo:** \	emplates/index.html\
- **Mudanças:** 
  1. Aplicada a classe \.pulp-btn-gold\ ao botão 'Entrar' (Ação Principal).
  2. Aplicada a classe \.pulp-btn-blue\ ao botão 'Cadastrar' (Ação Secundária diferenciada).
  3. Adicionados ícones representativos (sign-in-alt e user-plus) para reforçar a semântica Noir.
- **Motivo:** Manter a consistência visual do sistema pílula luminosa em todos os pontos de entrada do site.


## [2026-05-19] - Passo 5.7: Refino de Cores e Banner Mobile
- **Arquivos:** \static/css/style.css\, \	emplates/index.html\
- **Mudanças:** 
  1. Criada a classe \.pulp-btn-red\ utilizando o Vermelho Igreja (\--church-red\) para o botão 'Cadastrar', garantindo harmonia com o site.
  2. Ajustado o padding superior do banner mobile de 6rem para 3rem, elevando o conteúdo.
  3. Alterado o alinhamento vertical do banner no mobile para \lex-start\ para melhor aproveitamento da primeira dobra.
- **Motivo:** Melhorar a integração cromática do botão secundário e o equilíbrio visual no mobile.


## [2026-05-19] - Passo 5.8: Ajuste de Posicionamento Vertical Mobile (Banner)
- **Arquivo:** \	emplates/index.html\
- **Mudanças:** 
  1. Padding superior reduzido para 1rem no mobile, elevando o conteúdo drasticamente.
  2. Margem superior da logo no mobile reduzida para 0.5rem para ganho de espaço.
  3. Alinhamento vertical mantido em \lex-start\ para priorizar a visualização imediata da logo e CTAs.


## [2026-05-19] - Passo 6: Refino da Navbar e Padronização de Dropdowns
- **Arquivo:** \static/css/style.css\
- **Mudanças:** 
  1. Navbar compactada: Logo reduzida para 50px, títulos ajustados (0.8rem/1.2rem) e padding reduzido para 5px.
  2. Dropdowns padronizados: Fundo verde escuro (#0b2e1f), borda dourada de 2px e efeito hover com fundo dourado e texto preto.
- **Motivo:** Otimização de espaço vertical em tela e consistência visual nos componentes de navegação.

