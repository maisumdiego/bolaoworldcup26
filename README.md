# ⚽ Bolão da Cabeça 2026

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-F59E0B?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-064E3B?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Backend-0f172a?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-E11D48?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-Pulp_Noir-F59E0B?style=for-the-badge)

O **Bolão da Cabeça 2026** é uma aplicação web completa desenvolvida para gerenciar apostas esportivas da Copa do Mundo de 2026. Fugindo de soluções genéricas, o projeto consolida uma arquitetura de dados analítica, algoritmos de chaveamento dinâmico e um *Design System* autoral inspirado na estética *Pulp Noir*.

Não é apenas um formulário de palpites; é um motor de regras de negócio complexas rodando de forma fluida.

---

## 🏗️ Modelagem de Dados Analítica

Para suportar consultas rápidas e escalabilidade, o banco de dados (PostgreSQL + SQLAlchemy) foi desenhado adotando conceitos de modelagem dimensional. A separação clara entre dimensões e fatos garante integridade e facilita a extração de métricas de performance:

- **Dimensões (`dim_`)**: Tabelas como `dim_users`, `dim_teams` e `dim_games` armazenam dados estruturais e metadados.
- **Fatos (`fact_`)**: Tabelas como `fact_predictions` (histórico imutável de palpites) e `fact_group_standings` (agregados de performance dos times).

## ⚙️ Engine de Simulação e Regras de Negócio

O backend em **Python (Flask)** não atua apenas como uma API, mas como o árbitro central de todo o fluxo da Copa do Mundo.

### 1. Algoritmo de Classificação e Desempate
A cada apito final, a função de cálculo de grupos recalcula instantaneamente as tabelas. Os critérios de desempate da FIFA são aplicados de forma hierárquica e automatizada:
`Pontos Totais ➔ Saldo de Gols ➔ Gols Pró`

### 2. Chaveamento Dinâmico de Mata-Mata
O sistema elimina o trabalho manual após a fase de grupos. Através de um mapeamento por *placeholders* algébricos (ex: `1A` vs `2B`, `W73` vs `W74`), o projeto detecta o encerramento da primeira fase e **injeta os classificados** diretamente em suas respectivas chaves nas rodadas eliminatórias. O avanço pelas chaves subsequentes também é automático, suportando até mesmo vitórias decididas nos pênaltis.

### 3. Motor de Pontuação de Palpites
A avaliação dos palpites segue uma lógica condicional estrita de 3 níveis de acerto:
- **Na Mosca (5 pts):** Acerto exato do placar das duas equipes.
- **Parcial (3 pts):** Acerto da tendência (vitória/empate) mais o acerto do número de gols de apenas um dos times.
- **Tendência (2 pts):** Acerto apenas do resultado final da partida, errando o placar.

## 🎨 Design System: A Estética "Pulp Noir"

No frontend, a base de estruturação do **Bootstrap 5** foi customizada para garantir uma identidade visual própria e imersiva. O DOM é manipulado de forma cirúrgica com **JavaScript Vanilla** e templates **Jinja2**, garantindo leveza.

- **Paleta Restrita e Impactante:** Uso intensivo de *Verde Noir* (`#0f172a`, `#064e3b`), *Ouro Pulp* (`#F59E0B`) para destaques de interação e *Vermelho Igreja* (`#E11D48`) para sombreamentos e alertas.
- **Sombreamento Sólido (Hard Shadows):** Elementos UI, como botões e cards de jogos, utilizam sombras sólidas e profundas, remetendo ao estilo de quadrinhos retro e interfaces *arcade*.
- **Renderização Dinâmica:** Pódios e rankings são totalmente responsivos, calculados via CSS Flexbox/Grid, manipulando dinamicamente a propriedade `order` para garantir que o 1º lugar esteja sempre no topo ou ao centro, independentemente do dispositivo do usuário.

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Roteamento, autenticação (Flask-Login) e processamento das regras de negócio. |
| **Banco de Dados** | PostgreSQL | Persistência relacional otimizada. |
| **ORM** | SQLAlchemy | Abstração do banco e mapeamento do esquema dimensional. |
| **Frontend** | HTML5, CSS3, JS, Bootstrap 5 | Renderização do painel via Jinja2 e controle assíncrono de palpites. |
| **Integrações** | Cloudinary | Upload, armazenamento e entrega otimizada das fotos de perfil dos usuários. |

---

## 🚀 Como Executar Localmente

**1. Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/world-cup-2026.git
cd world-cup-2026
```

**2. Configure o ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Variáveis de Ambiente:**
Crie um arquivo `.env` na raiz do projeto com as chaves base:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/bolao_db
SECRET_KEY=sua_chave_secreta
EMAIL_ADMIN=seu_email_admin
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

**4. Inicie a aplicação:**
```bash
python app.py
```
Acesse `http://localhost:5000` para visualizar e interagir com o sistema.

---

*“A glória aguarda os melhores palpites.”* 🏆
