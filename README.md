# SILVESS - Sistema de Gestão de Restaurantes

![SILVESS Logo](frontend/assets/images/silvess_logo.png)

Sistema completo e profissional para gestão de restaurantes, com controle de estoque, fichas técnicas detalhadas com gramatura, inventário editável e cardápio digital com QR codes.

## 🚀 Características Principais

### ✨ Fichas Técnicas Detalhadas
- Cadastro de pratos com **gramatura precisa** de cada ingrediente
- Cálculo automático de custos por porção
- Margem de lucro calculada automaticamente
- Modo de preparo, tempo e validade
- Informações nutricionais (opcional)

### 📦 Gestão de Estoque Inteligente
- Controle completo de ingredientes
- Alertas de estoque mínimo
- Movimentações automáticas ao registrar vendas
- Histórico completo de entradas e saídas

### 📋 Inventário Editável
- Geração automática de inventário mensal
- **Contagem física editável** com correção de divergências
- Cálculo automático de diferenças
- Ajuste de estoque com um clique
- Fechamento de inventário para controle

### 📱 Cardápio Digital com QR Codes
- Criação de cardápios personalizados
- **QR codes únicos por mesa**
- Visualização responsiva para clientes
- Atualização em tempo real de disponibilidade
- Administração centralizada de todos os cardápios

### 📊 Dashboard Profissional
- Visão geral de vendas e estoque
- Gráficos e indicadores em tempo real
- Relatórios customizáveis
- Interface intuitiva e moderna

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.11** - Linguagem principal
- **Flask** - Framework web
- **SQLite** - Banco de dados (desenvolvimento)
- **PostgreSQL** - Banco de dados (produção)
- **JWT** - Autenticação segura
- **QRCode** - Geração de QR codes
- **Gunicorn** - Servidor WSGI

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização moderna
- **JavaScript (Vanilla)** - Interatividade
- **Font Awesome** - Ícones
- **Responsive Design** - Mobile-first

## 📋 Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes Python)
- Git
- Navegador web moderno

## 🔧 Instalação Local

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/silvess.git
cd silvess
```

### 2. Configure o Backend

```bash
cd backend

# Crie um ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Inicialize o banco de dados
python models/database.py

# Inicie o servidor
python app.py
```

O backend estará disponível em `http://localhost:5000`

### 3. Configure o Frontend

```bash
cd ../frontend

# Abra o arquivo js/api.js e configure a URL do backend
# Se estiver rodando localmente, já está configurado

# Abra o arquivo index.html ou login.html no navegador
# Ou use um servidor HTTP simples:
python -m http.server 8000
```

O frontend estará disponível em `http://localhost:8000`

### 4. Crie o usuário administrador

No primeiro acesso, descomente a linha no `login.html` para criar o usuário admin padrão:
- **Email**: admin@silvess.com
- **Senha**: admin123

⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 🚀 Deploy em Produção

### Backend no Render

1. Crie uma conta em [Render.com](https://render.com)

2. Crie um novo **Web Service**

3. Conecte seu repositório GitHub

4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

5. Adicione as variáveis de ambiente:
   ```
   SECRET_KEY=sua-chave-secreta-aqui
   JWT_SECRET=seu-jwt-secret-aqui
   DEBUG=False
   FRONTEND_URL=https://seu-usuario.github.io/silvess
   ```

6. Deploy automático será feito a cada push

### Frontend no GitHub Pages

1. Crie um repositório no GitHub

2. Faça push do código:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/seu-usuario/silvess.git
git push -u origin main
```

3. Vá em **Settings** > **Pages**

4. Selecione:
   - **Source**: Deploy from a branch
   - **Branch**: main
   - **Folder**: /frontend

5. Aguarde alguns minutos e seu site estará em:
   `https://seu-usuario.github.io/silvess`

6. **IMPORTANTE**: Atualize a URL do backend em `frontend/js/api.js`:
```javascript
const API_BASE_URL = 'https://seu-backend.onrender.com/api';
```

## 📚 Documentação da API

### Autenticação

#### POST /api/auth/register
Registra um novo usuário
```json
{
  "nome": "Nome do Usuário",
  "email": "email@exemplo.com",
  "senha": "senha123",
  "perfil": "admin" // ou "usuario"
}
```

#### POST /api/auth/login
Realiza login
```json
{
  "email": "email@exemplo.com",
  "senha": "senha123"
}
```

#### GET /api/auth/me
Retorna dados do usuário autenticado (requer token)

### Ingredientes

#### GET /api/ingredientes
Lista todos os ingredientes

#### POST /api/ingredientes
Cria um novo ingrediente
```json
{
  "nome": "Farinha de Trigo",
  "unidade_medida": "kg",
  "custo_unitario": 5.50,
  "estoque_atual": 10,
  "estoque_minimo": 2,
  "fornecedor": "Fornecedor XYZ"
}
```

#### POST /api/ingredientes/{id}/estoque
Atualiza estoque de um ingrediente
```json
{
  "tipo": "entrada", // ou "saida"
  "quantidade": 5,
  "observacao": "Compra mensal"
}
```

### Fichas Técnicas

#### GET /api/fichas
Lista todas as fichas técnicas

#### POST /api/fichas
Cria uma nova ficha técnica
```json
{
  "nome_prato": "Bolo de Chocolate",
  "categoria": "Sobremesa",
  "descricao": "Delicioso bolo de chocolate",
  "porcoes": 8,
  "tempo_preparo": 60,
  "modo_preparo": "Misture todos os ingredientes...",
  "preco_venda": 45.00,
  "ingredientes": [
    {
      "ingrediente_id": 1,
      "quantidade_gramas": 500
    },
    {
      "ingrediente_id": 2,
      "quantidade_gramas": 200
    }
  ]
}
```

### Inventário

#### POST /api/inventario/gerar
Gera um novo inventário
```json
{
  "data_inventario": "2024-01-31"
}
```

#### PUT /api/inventario/{id}
Atualiza um item do inventário
```json
{
  "quantidade_fisica": 8.5,
  "observacoes": "Diferença devido a quebra",
  "ajustar_estoque": true
}
```

#### POST /api/inventario/fechar/{data}
Fecha o inventário de uma data

### Cardápios

#### GET /api/cardapio
Lista todos os cardápios (público)

#### POST /api/cardapio
Cria um novo cardápio
```json
{
  "nome": "Cardápio de Verão",
  "data": "2024-01-15",
  "descricao": "Pratos leves e refrescantes",
  "ativo": 1,
  "pratos": [
    {
      "ficha_tecnica_id": 1,
      "disponivel": 1,
      "ordem": 0
    }
  ]
}
```

### Mesas

#### GET /api/cardapio/mesas
Lista todas as mesas

#### POST /api/cardapio/mesas
Cria uma nova mesa
```json
{
  "numero": 1,
  "cardapio_id": 1,
  "ativo": 1
}
```

#### GET /api/cardapio/mesas/{id}/qrcode
Obtém o QR code de uma mesa

## 🔐 Segurança

- Autenticação via JWT
- Senhas com hash bcrypt
- CORS configurado
- Validação de entrada com Zod
- HTTPS obrigatório em produção
- Variáveis de ambiente protegidas

## 📱 Funcionalidades Mobile

O sistema é totalmente responsivo e funciona perfeitamente em:
- Smartphones
- Tablets
- Desktops

O cardápio digital foi especialmente otimizado para visualização em dispositivos móveis.

## 🎯 Roadmap Futuro

- [ ] Integração com sistemas de pagamento
- [ ] Relatórios avançados com gráficos
- [ ] Aplicativo mobile nativo
- [ ] Integração com impressoras térmicas
- [ ] Sistema de cupom fiscal
- [ ] Controle de acesso por usuário
- [ ] Backup automático do banco de dados
- [ ] Multi-idiomas
- [ ] Tema escuro

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do email: suporte@silvess.com

## 🙏 Agradecimentos

Desenvolvido com ❤️ para ajudar restaurantes a gerenciar seus negócios de forma profissional e eficiente.

---

**SILVESS** - Sistema de Gestão de Restaurantes
© 2024 - Todos os direitos reservados
