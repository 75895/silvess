# 🚀 Guia Completo de Deploy - SILVESS

Este guia irá ajudá-lo a fazer o deploy do sistema SILVESS no Render (backend) e GitHub Pages (frontend).

## 📋 Pré-requisitos

- Conta no GitHub
- Conta no Render (gratuita)
- Git instalado localmente
- Código do SILVESS pronto

## Parte 1: Preparar o Repositório no GitHub

### 1.1 Criar Repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no botão **"New"** para criar um novo repositório
3. Configure:
   - **Repository name**: `silvess`
   - **Description**: "Sistema de Gestão de Restaurantes"
   - **Visibility**: Public (necessário para GitHub Pages gratuito)
   - ✅ Add a README file
   - ✅ Add .gitignore: Python
   - License: MIT (opcional)
4. Clique em **"Create repository"**

### 1.2 Fazer Upload do Código

No terminal, dentro da pasta do projeto:

```bash
# Inicializar repositório Git
git init

# Adicionar todos os arquivos
git add .

# Fazer o primeiro commit
git commit -m "Initial commit - Sistema SILVESS completo"

# Adicionar o repositório remoto
git remote add origin https://github.com/SEU-USUARIO/silvess.git

# Enviar para o GitHub
git branch -M main
git push -u origin main
```

## Parte 2: Deploy do Backend no Render

### 2.1 Criar Conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em **"Get Started"**
3. Faça signup com sua conta do GitHub (recomendado)

### 2.2 Criar Web Service

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório GitHub `silvess`
4. Configure o serviço:

**Configurações Básicas:**
- **Name**: `silvess-backend`
- **Region**: Oregon (US West) - mais próximo
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Plano:**
- Selecione **Free** (gratuito)

### 2.3 Configurar Variáveis de Ambiente

Na seção **Environment**, adicione as seguintes variáveis:

```
SECRET_KEY = [clique em "Generate" para gerar automaticamente]
JWT_SECRET = [clique em "Generate" para gerar automaticamente]
DEBUG = False

DATABASE_PATH = /opt/render/project/src/silvess.db
FRONTEND_URL = https://SEU-USUARIO.github.io/silvess
```

⚠️ **IMPORTANTE**: Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub.

### 2.4 Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o deploy (5-10 minutos na primeira vez)
3. Quando concluído, você verá: ✅ **Live**
4. Anote a URL do seu backend: `https://silvess-backend.onrender.com`

### 2.5 Testar o Backend

Acesse no navegador:
```
https://silvess-backend.onrender.com/health
```

Você deve ver:
```json
{"status": "ok"}
```

## Parte 3: Deploy do Frontend no GitHub Pages

### 3.1 Atualizar URL do Backend

1. Abra o arquivo `frontend/js/api.js`
2. Localize a linha:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : 'https://seu-backend.onrender.com/api';
```

3. Substitua `https://seu-backend.onrender.com/api` pela URL real do seu backend:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : 'https://silvess-backend.onrender.com/api';
```

4. Salve o arquivo

### 3.2 Commit e Push

```bash
git add frontend/js/api.js
git commit -m "Atualizar URL do backend para produção"
git push origin main
```

### 3.3 Configurar GitHub Pages

1. Acesse seu repositório no GitHub
2. Vá em **Settings** (Configurações)
3. No menu lateral, clique em **Pages**
4. Em **Source**, selecione:
   - **Branch**: `main`
   - **Folder**: `/frontend` (se disponível) ou `/` (root)
5. Clique em **Save**
6. Aguarde 2-3 minutos

### 3.4 Ajustar Estrutura (se necessário)

Se o GitHub Pages não encontrar os arquivos, você precisa mover o conteúdo do frontend para a raiz:

```bash
# Criar branch gh-pages
git checkout -b gh-pages

# Mover arquivos do frontend para raiz
cp -r frontend/* .

# Commit
git add .
git commit -m "Preparar para GitHub Pages"
git push origin gh-pages
```

Depois, nas configurações do GitHub Pages, selecione a branch `gh-pages`.

### 3.5 Atualizar FRONTEND_URL no Render

1. Volte ao Render
2. Acesse seu serviço `silvess-backend`
3. Vá em **Environment**
4. Atualize a variável `FRONTEND_URL` com a URL correta:
```
FRONTEND_URL = https://SEU-USUARIO.github.io/silvess
```
5. Clique em **Save Changes**
6. O serviço será reiniciado automaticamente

## Parte 4: Configuração Inicial do Sistema

### 4.1 Acessar o Sistema

Acesse: `https://SEU-USUARIO.github.io/silvess/login.html`

### 4.2 Criar Usuário Administrador

**Opção 1: Via Código (Recomendado)**

1. Abra o arquivo `frontend/login.html`
2. Localize a linha comentada no final:
```javascript
// createDefaultAdmin();
```
3. Descomente temporariamente:
```javascript
createDefaultAdmin();
```
4. Commit e push:
```bash
git add frontend/login.html
git commit -m "Criar admin padrão"
git push origin main
```
5. Acesse a página de login
6. O usuário admin será criado automaticamente
7. **Comente a linha novamente** e faça push

**Credenciais padrão:**
- Email: `admin@silvess.com`
- Senha: `admin123`

⚠️ **IMPORTANTE**: Altere a senha imediatamente após o primeiro login!

**Opção 2: Via API (Avançado)**

Use Postman ou curl:
```bash
curl -X POST https://silvess-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Administrador",
    "email": "admin@silvess.com",
    "senha": "admin123",
    "perfil": "admin"
  }'
```

### 4.3 Primeiro Login

1. Acesse a página de login
2. Entre com as credenciais criadas
3. Você será redirecionado para o dashboard

### 4.4 Configuração Inicial

1. **Cadastrar Ingredientes**:
   - Vá em "Ingredientes"
   - Clique em "Novo Ingrediente"
   - Cadastre seus ingredientes básicos

2. **Criar Fichas Técnicas**:
   - Vá em "Fichas Técnicas"
   - Clique em "Nova Ficha Técnica"
   - Crie os pratos do seu cardápio

3. **Configurar Mesas**:
   - Vá em "Mesas & QR Codes"
   - Crie as mesas do seu restaurante

4. **Criar Cardápio**:
   - Vá em "Cardápios"
   - Crie o cardápio do dia
   - Associe às mesas

5. **Gerar QR Codes**:
   - Em "Mesas & QR Codes"
   - Clique em "Ver QR Code" para cada mesa
   - Imprima e coloque nas mesas

## Parte 5: Manutenção e Atualizações

### 5.1 Atualizar o Sistema

Sempre que fizer alterações:

```bash
# Adicionar mudanças
git add .

# Commit
git commit -m "Descrição das mudanças"

# Push
git push origin main
```

- **Backend**: Deploy automático no Render (2-5 minutos)
- **Frontend**: Atualização automática no GitHub Pages (1-2 minutos)

### 5.2 Monitoramento

**Backend (Render):**
- Acesse o dashboard do Render
- Veja logs em tempo real
- Monitore uso de recursos

**Frontend (GitHub Pages):**
- Acesse as configurações do repositório
- Veja status do deploy em "Actions"

### 5.3 Backup do Banco de Dados

⚠️ **IMPORTANTE**: O Render Free Tier pode perder dados após inatividade.

Para fazer backup:

1. Acesse o shell do Render:
   - Dashboard > seu serviço > Shell
2. Execute:
```bash
cp silvess.db silvess_backup_$(date +%Y%m%d).db
```

**Recomendação**: Configure backup automático ou use PostgreSQL (plano pago).

## Parte 6: Troubleshooting

### Problema: Backend não inicia

**Solução:**
1. Verifique os logs no Render
2. Confirme que todas as dependências estão em `requirements.txt`
3. Verifique as variáveis de ambiente

### Problema: Frontend não carrega dados

**Solução:**
1. Abra o Console do navegador (F12)
2. Verifique se há erros de CORS
3. Confirme que a URL do backend está correta em `api.js`
4. Teste o backend diretamente: `https://seu-backend.onrender.com/health`

### Problema: QR Codes não funcionam

**Solução:**
1. Verifique se `FRONTEND_URL` está correto no Render
2. Confirme que o cardápio está associado à mesa
3. Teste o link do QR Code manualmente

### Problema: GitHub Pages mostra 404

**Solução:**
1. Verifique se o deploy foi concluído (Settings > Pages)
2. Confirme que os arquivos estão na pasta correta
3. Aguarde alguns minutos após o push

## 📞 Suporte

Se precisar de ajuda:
1. Verifique os logs no Render
2. Verifique o Console do navegador
3. Revise este guia
4. Abra uma issue no GitHub

## ✅ Checklist Final

- [ ] Repositório criado no GitHub
- [ ] Código enviado para o GitHub
- [ ] Backend deployado no Render
- [ ] Variáveis de ambiente configuradas
- [ ] Backend testado e funcionando
- [ ] URL do backend atualizada no frontend
- [ ] Frontend deployado no GitHub Pages
- [ ] FRONTEND_URL atualizada no Render
- [ ] Usuário admin criado
- [ ] Primeiro login realizado
- [ ] Senha padrão alterada
- [ ] Sistema testado end-to-end

## 🎉 Parabéns!

Seu sistema SILVESS está no ar e pronto para uso!

Acesse: `https://SEU-USUARIO.github.io/silvess`

---

**SILVESS** - Sistema de Gestão de Restaurantes
