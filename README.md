# ⚽ Bolão da Cabeça 2026

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-F59E0B?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-Python_|_Flask_|_PostgreSQL-064E3B?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-Pulp_Noir_Style-E11D48?style=for-the-badge)

O **Bolão da Cabeça 2026** é uma plataforma de apostas esportivas premium dedicada à Copa do Mundo de 2026. Com uma estética inspirada no movimento *Pulp Noir*, o projeto oferece uma experiência visual cinematográfica aliada a uma lógica competitiva rigorosa para determinar quem é o verdadeiro mestre dos palpites.

---

## 🎨 A Experiência "Pulp Noir"

Diferente de bolões convencionais, este projeto foca na imersão visual:
- **Identidade Visual:** Paleta de cores baseada em *Verde Noir*, *Ouro Pulp* e *Vermelho Igreja*.
- **Tipografia Brutalista:** Uso de fontes *Bungee* para títulos arcade e *Montserrat* para leitura limpa.
- **Componentes Dinâmicos:** Cards com sombras sólidas, pódios metálicos e interfaces sem degradês desnecessários para um visual sólido e impactante.

## ⚙️ Funcionalidades Principais

- **Mesa de Palpites:** Visualize os palpites de outros participantes em tempo real (após o limite de aposta).
- **Ranking Inteligente:** Sistema de pontuação com critérios de desempate técnicos (Exatos > Parciais > Tendência).
- **Raio-X da Copa:** Dossiês completos sobre cada seleção participante via integração com APIs externas.
- **Exportação Premium:** Geração de imagens automáticas otimizadas para Instagram/WhatsApp Stories com o estado atual do ranking e pódio.
- **Painel Administrativo:** Controle total de jogos, resultados, chaveamento automatizado de mata-mata e aprovação dinâmica de usuários.

## 📊 Sistema de Pontuação

A competitividade é garantida por um motor de pontuação preciso:

| Acerto | Descrição | Pontos |
| :--- | :--- | :---: |
| **Na Mosca** | Placar exato do jogo | **5** |
| **Parcial** | Vencedor + Gols de um dos times | **3** |
| **Tendência** | Apenas o vencedor ou empate | **2** |

## 🚀 Tecnologias

- **Backend:** Python / Flask
- **Banco de Dados:** PostgreSQL (Produção) / SQLite (Dev)
- **Frontend:** Jinja2 / CSS3 Custom / JavaScript Vanilla
- **Cloud:** Cloudinary (Gestão de Mídia)
- **Deploy:** Estrutura preparada para ambientes como Railway/Render

---

## 🛠️ Instalação e Desenvolvimento

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/world-cup-2026.git
   ```

2. **Configure o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   pip install -r requirements.txt
   ```

3. **Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz do projeto com:
   ```env
   DATABASE_URL=seu_db_url
   SECRET_KEY=sua_chave_secreta
   EMAIL_ADMIN=seu_email_admin
   CLOUDINARY_CLOUD_NAME=seu_cloud_name
   CLOUDINARY_API_KEY=sua_api_key
   CLOUDINARY_API_SECRET=seu_api_secret
   ```

4. **Inicie a aplicação:**
   ```bash
   python app.py
   ```

---

*“A glória aguarda os melhores palpites.”* 🏆
