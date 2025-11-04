# ⚡ Quick Start - SILVESS

Guia rápido para começar a usar o sistema em 5 minutos!

## 🚀 Opção 1: Rodar Localmente (Desenvolvimento)

### Passo 1: Backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

Backend rodando em: `http://localhost:5000`

### Passo 2: Frontend

```bash
cd frontend
python -m http.server 8000
```

Frontend rodando em: `http://localhost:8000`

### Passo 3: Primeiro Acesso

1. Abra: `http://localhost:8000/login.html`
2. Crie usuário admin (veja instruções no README)
3. Login: `admin@silvess.com` / `admin123`

## ☁️ Opção 2: Deploy em Produção

### Backend no Render

1. Crie conta em [render.com](https://render.com)
2. New Web Service → Conecte GitHub
3. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Root Directory: `backend`
4. Adicione variáveis de ambiente (veja DEPLOY_GUIDE.md)

### Frontend no GitHub Pages

1. Push código para GitHub
2. Settings → Pages
3. Source: main branch / frontend folder
4. Aguarde 2-3 minutos

## 📱 Testar Funcionalidades

### 1. Cadastrar Ingrediente
Dashboard → Ingredientes → Novo Ingrediente

### 2. Criar Ficha Técnica
Dashboard → Fichas Técnicas → Nova Ficha
- Adicione ingredientes com gramatura
- Veja cálculo automático de custos

### 3. Gerar QR Code
Dashboard → Mesas & QR Codes → Nova Mesa → Ver QR Code

### 4. Fazer Inventário
Dashboard → Inventário → Gerar Novo
- Digite contagem física
- Veja diferenças automaticamente

## 📚 Documentação Completa

- **README.md**: Visão geral e instalação
- **DEPLOY_GUIDE.md**: Deploy passo a passo
- **MANUAL_USUARIO.md**: Guia completo de uso
- **RESUMO_EXECUTIVO.md**: Visão técnica

## 🆘 Problemas Comuns

**Backend não inicia?**
- Verifique se Python 3.11 está instalado
- Instale dependências: `pip install -r requirements.txt`

**Frontend não carrega dados?**
- Verifique URL em `frontend/js/api.js`
- Confirme que backend está rodando

**Erro de CORS?**
- Backend deve estar configurado com CORS
- Verifique `FRONTEND_URL` nas variáveis de ambiente

## ✅ Checklist Rápido

- [ ] Python 3.11 instalado
- [ ] Dependências instaladas
- [ ] Backend rodando
- [ ] Frontend acessível
- [ ] Usuário admin criado
- [ ] Primeiro login realizado

## 🎯 Próximos Passos

1. Cadastre seus ingredientes
2. Crie fichas técnicas dos pratos
3. Configure as mesas
4. Gere QR codes
5. Faça primeiro inventário

---

**Pronto para usar! 🍽️**

Para dúvidas, consulte a documentação completa.
