// ========== CONFIGURAÇÃO DA API ==========
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : 'https://seu-backend.onrender.com/api';

// ========== GERENCIAMENTO DE TOKEN ==========
const TokenManager = {
    get: () => localStorage.getItem('silvess_token'),
    set: (token) => localStorage.setItem('silvess_token', token),
    remove: () => localStorage.removeItem('silvess_token'),
    isValid: () => !!TokenManager.get()
};

// ========== GERENCIAMENTO DE USUÁRIO ==========
const UserManager = {
    get: () => {
        const user = localStorage.getItem('silvess_user');
        return user ? JSON.parse(user) : null;
    },
    set: (user) => localStorage.setItem('silvess_user', JSON.stringify(user)),
    remove: () => localStorage.removeItem('silvess_user'),
    isAuthenticated: () => TokenManager.isValid() && UserManager.get() !== null
};

// ========== CLIENTE HTTP ==========
class HttpClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const token = TokenManager.get();

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    // Token inválido ou expirado
                    TokenManager.remove();
                    UserManager.remove();
                    window.location.href = '/login.html';
                }
                throw new Error(data.error || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// ========== INSTÂNCIA DO CLIENTE ==========
const api = new HttpClient(API_BASE_URL);

// ========== SERVIÇOS DE API ==========
const AuthService = {
    login: (email, senha) => api.post('/auth/login', { email, senha }),
    register: (nome, email, senha, perfil = 'usuario') => 
        api.post('/auth/register', { nome, email, senha, perfil }),
    getCurrentUser: () => api.get('/auth/me'),
    changePassword: (senha_atual, senha_nova) => 
        api.post('/auth/change-password', { senha_atual, senha_nova }),
    logout: () => {
        TokenManager.remove();
        UserManager.remove();
        window.location.href = '/login.html';
    }
};

const IngredientesService = {
    list: (params = {}) => api.get('/ingredientes', params),
    getById: (id) => api.get(`/ingredientes/${id}`),
    create: (data) => api.post('/ingredientes', data),
    update: (id, data) => api.put(`/ingredientes/${id}`, data),
    delete: (id) => api.delete(`/ingredientes/${id}`),
    atualizarEstoque: (id, tipo, quantidade, observacao = '') => 
        api.post(`/ingredientes/${id}/estoque`, { tipo, quantidade, observacao }),
    getEstoqueBaixo: () => api.get('/ingredientes/estoque-baixo')
};

const FichasService = {
    list: (params = {}) => api.get('/fichas', params),
    getById: (id) => api.get(`/fichas/${id}`),
    create: (data) => api.post('/fichas', data),
    update: (id, data) => api.put(`/fichas/${id}`, data),
    delete: (id) => api.delete(`/fichas/${id}`),
    getCategorias: () => api.get('/fichas/categorias')
};

const InventarioService = {
    list: (params = {}) => api.get('/inventario', params),
    gerar: (data_inventario) => api.post('/inventario/gerar', { data_inventario }),
    atualizar: (id, quantidade_fisica, observacoes = '', ajustar_estoque = false) => 
        api.put(`/inventario/${id}`, { quantidade_fisica, observacoes, ajustar_estoque }),
    fechar: (data_inventario) => api.post(`/inventario/fechar/${data_inventario}`),
    reabrir: (data_inventario) => api.post(`/inventario/reabrir/${data_inventario}`),
    getRelatorio: (data_inventario) => api.get(`/inventario/relatorio/${data_inventario}`)
};

const CardapioService = {
    list: (params = {}) => api.get('/cardapio', params),
    getById: (id) => api.get(`/cardapio/${id}`),
    create: (data) => api.post('/cardapio', data),
    update: (id, data) => api.put(`/cardapio/${id}`, data),
    delete: (id) => api.delete(`/cardapio/${id}`),
    togglePratoDisponibilidade: (cardapio_id, prato_id, disponivel) => 
        api.put(`/cardapio/${cardapio_id}/prato/${prato_id}/disponibilidade`, { disponivel })
};

const MesasService = {
    list: () => api.get('/cardapio/mesas'),
    create: (data) => api.post('/cardapio/mesas', data),
    update: (id, data) => api.put(`/cardapio/mesas/${id}`, data),
    getQRCode: (id) => api.get(`/cardapio/mesas/${id}/qrcode`)
};

const DashboardService = {
    getStats: () => api.get('/dashboard/stats'),
    getVendas: (params = {}) => api.get('/dashboard/vendas', params),
    registrarVenda: (data) => api.post('/dashboard/vendas', data),
    getRelatorioVendas: (data_inicio, data_fim) => 
        api.get('/dashboard/relatorio/vendas', { data_inicio, data_fim }),
    getRelatorioEstoque: () => api.get('/dashboard/relatorio/estoque')
};

// ========== UTILITÁRIOS ==========
const Utils = {
    formatCurrency: (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    formatDate: (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pt-BR').format(date);
    },

    formatDateTime: (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'short'
        }).format(date);
    },

    showAlert: (message, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.style.minWidth = '300px';
        alertDiv.style.animation = 'slideIn 0.3s ease-out';

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => alertDiv.remove(), 300);
        }, 3000);
    },

    showLoading: (element) => {
        element.disabled = true;
        element.innerHTML = '<span class="loading"></span> Carregando...';
    },

    hideLoading: (element, originalText) => {
        element.disabled = false;
        element.innerHTML = originalText;
    },

    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// ========== PROTEÇÃO DE ROTAS ==========
function requireAuth() {
    if (!UserManager.isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

function redirectIfAuthenticated() {
    if (UserManager.isAuthenticated()) {
        window.location.href = '/dashboard.html';
        return true;
    }
    return false;
}

// ========== EXPORTAR PARA USO GLOBAL ==========
window.API = {
    Auth: AuthService,
    Ingredientes: IngredientesService,
    Fichas: FichasService,
    Inventario: InventarioService,
    Cardapio: CardapioService,
    Mesas: MesasService,
    Dashboard: DashboardService
};

window.TokenManager = TokenManager;
window.UserManager = UserManager;
window.Utils = Utils;
window.requireAuth = requireAuth;
window.redirectIfAuthenticated = redirectIfAuthenticated;
