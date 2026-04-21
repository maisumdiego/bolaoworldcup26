# ⚽ Bolão da Cabeça 2026

![GitHub version](https://img.shields.io/badge/version-1.0.0--v1-gold)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)

O **Bolão da Cabeça 2026** é uma plataforma completa de palpites para a Copa do Mundo, desenvolvida para proporcionar uma experiência competitiva e imersiva entre amigos. Com uma interface inspirada na estética *Pulp Noir* (Navy, Gold & Red), o sistema oferece desde a gestão de palpites até a automatização de chaveamentos de mata-mata.

---

## 🚀 Funcionalidades Principais

- **Gestão de Palpites**: Sistema de palpites dinâmico com filtros por data, grupo e fase da competição.
- **Ranking em Tempo Real**: Classificação automática dos participantes baseada em critérios de desempate técnicos (Pontos > Exatos > Parciais).
- **Mata-Mata Automatizado**: O sistema detecta o encerramento da fase de grupos e injeta automaticamente as seleções classificadas nas oitavas de final.
- **Raio-X da Copa**: Painel interativo que consome as APIs *REST Countries* e *Wikipedia* para fornecer dados históricos e geográficos sobre cada seleção.
- **Painel Administrativo**: Gestão completa de usuários (aprovação/revogação de acesso) e inserção de resultados oficiais.
- **Segurança**: Autenticação robusta com `Flask-Login` e criptografia de senhas com `Werkzeug`.

---

## 🛠️ Stack Tecnológica

- **Backend**: Python 3.9+ & Flask
- **Banco de Dados**: PostgreSQL (Arquitetura Dimensional: `dim_` e `fact_`)
- **Frontend**: Jinja2, Bootstrap 5, FontAwesome & AOS (Animate on Scroll)
- **Bibliotecas Chave**:
  - `SQLAlchemy`: ORM para mapeamento de dados.
  - `Pandas`: Utilizado nos scripts de ingestão de dados (`seed.py`).
  - `jQuery Bracket`: Renderização visual do chaveamento final.

---

## 📈 Sistema de Pontuação (Como pontuar)

O motor de cálculo do ranking segue regras rigorosas para premiar o conhecimento futebolístico:

- **+5 Pontos (Na Mosca)**: Acerto exato do placar.
- **+3 Pontos (Vencedor e Gols)**: Acerto do vencedor/empate e dos gols de um dos times.
- **+2 Pontos (Tendência)**: Acerto apenas do vencedor ou empate (tendência do jogo).

---

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Python instalado
- Banco de Dados PostgreSQL

### Passo a Passo

1. **Clone o repositório**:

   ```bash
   git clone [https://github.com/maisumdiego/bolaoworldcup26.git](https://github.com/maisumdiego/bolaoworldcup26.git)
   ```
2. **Instale as dependências**:

   ```
   pip install -r requirements.txt
   ```
3. **Configure as Variáveis de Ambiente (.env)** :

   ```
   DATABASE_URL=seu_link_postgresql
   SECRET_KEY=sua_chave_secreta
   EMAIL_ADMIN=seu_email@exemplo.com
   TZ=America/Sao_Paulo
   ```
4. **Inicialize o Banco e os Dados**:

   * Execute o script `bd.sql` no seu banco.
   * Popule as seleções e jogos: `python seed.py`.
   * Acesse a rota `/admin/init_grupos` (logado como admin) para gerar a classificação inicial.

---

## 👤 Autor

Desenvolvido por **Diego Gonçalves Ferreira** – Analista de Dados focado em soluções escaláveis e visualização de dados.
