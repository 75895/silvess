// Verificar autenticação
if (!requireAuth()) {
    throw new Error('Não autenticado');
}

// ========== ELEMENTOS DO DOM ==========
const sidebar = document.getElementById('sidebar');
const mobileToggle = document.getElementById('mobileToggle');
const menuItems = document.querySelectorAll('.menu-item');
const btnLogout = document.getElementById('btnLogout');
const btnRefresh = document.getElementById('btnRefresh');
const pageTitle = document.getElementById('pageTitle');
const breadcrumb = document.getElementById('breadcrumb');
const contentArea = document.getElementById('contentArea');

// Stats
const statIngredientes = document.getElementById('statIngredientes');
const statEstoqueBaixo = document.getElementById('statEstoqueBaixo');
const statFichas = document.getElementById('statFichas');
const statVendasHoje = document.getElementById('statVendasHoje');
const statVendasHojeQtd = document.getElementById('statVendasHojeQtd');

// User info
const userName = document.getElementById('userName');
const userEmail = document.getElementById('userEmail');
const userAvatar = document.getElementById('userAvatar');

// ========== INICIALIZAÇÃO ==========
document.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    loadStats();
    setupEventListeners();
});

// ========== INFORMAÇÕES DO USUÁRIO ==========
function loadUserInfo() {
    const user = UserManager.get();
    if (user) {
        userName.textContent = user.nome;
        userEmail.textContent = user.email;
        userAvatar.textContent = user.nome.charAt(0).toUpperCase();
    }
}

// ========== CARREGAR ESTATÍSTICAS ==========
async function loadStats() {
    try {
        const stats = await API.Dashboard.getStats();
        
        statIngredientes.textContent = stats.ingredientes.total;
        statEstoqueBaixo.textContent = stats.ingredientes.estoque_baixo;
        statFichas.textContent = stats.fichas_tecnicas.total;
        statVendasHoje.textContent = Utils.formatCurrency(stats.vendas_hoje.valor_total);
        statVendasHojeQtd.textContent = `${stats.vendas_hoje.total} vendas`;
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        Utils.showAlert('Erro ao carregar estatísticas', 'danger');
    }
}

// ========== EVENT LISTENERS ==========
function setupEventListeners() {
    // Mobile toggle
    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    // Menu items
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navigateToPage(page);
            
            // Atualizar menu ativo
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Fechar sidebar no mobile
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
            }
        });
    });

    // Logout
    btnLogout.addEventListener('click', () => {
        if (confirm('Deseja realmente sair?')) {
            API.Auth.logout();
        }
    });

    // Refresh
    btnRefresh.addEventListener('click', () => {
        loadStats();
        Utils.showAlert('Dados atualizados!', 'success');
    });
}

// ========== NAVEGAÇÃO ==========
function navigateToPage(page) {
    const titles = {
        home: 'Dashboard',
        ingredientes: 'Ingredientes',
        fichas: 'Fichas Técnicas',
        inventario: 'Inventário',
        cardapio: 'Cardápios',
        mesas: 'Mesas & QR Codes',
        vendas: 'Vendas',
        relatorios: 'Relatórios'
    };

    pageTitle.textContent = titles[page] || 'Dashboard';
    breadcrumb.textContent = `Home / ${titles[page] || 'Dashboard'}`;

    // Carregar conteúdo da página
    switch(page) {
        case 'home':
            loadHomePage();
            break;
        case 'ingredientes':
            loadIngredientesPage();
            break;
        case 'fichas':
            loadFichasPage();
            break;
        case 'inventario':
            loadInventarioPage();
            break;
        case 'cardapio':
            loadCardapioPage();
            break;
        case 'mesas':
            loadMesasPage();
            break;
        case 'vendas':
            loadVendasPage();
            break;
        case 'relatorios':
            loadRelatoriosPage();
            break;
        default:
            loadHomePage();
    }
}

// ========== PÁGINAS ==========
function loadHomePage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Bem-vindo ao SILVESS</h2>
            </div>
            <div class="section-body">
                <p style="font-size: 18px; color: var(--text-secondary); line-height: 1.8;">
                    Sistema completo de gestão para restaurantes. Utilize o menu lateral para navegar entre as funcionalidades:
                </p>
                <div class="row mt-4">
                    <div class="col-6">
                        <div class="card">
                            <h3 style="color: var(--primary-color); margin-bottom: 15px;">
                                <i class="fas fa-box"></i> Gestão de Estoque
                            </h3>
                            <p>Controle completo de ingredientes, movimentações e alertas de estoque mínimo.</p>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card">
                            <h3 style="color: var(--primary-color); margin-bottom: 15px;">
                                <i class="fas fa-utensils"></i> Fichas Técnicas
                            </h3>
                            <p>Cadastre pratos com gramatura detalhada e cálculo automático de custos.</p>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card">
                            <h3 style="color: var(--primary-color); margin-bottom: 15px;">
                                <i class="fas fa-clipboard-list"></i> Inventário
                            </h3>
                            <p>Realize inventários mensais editáveis e corrija divergências facilmente.</p>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card">
                            <h3 style="color: var(--primary-color); margin-bottom: 15px;">
                                <i class="fas fa-qrcode"></i> QR Codes
                            </h3>
                            <p>Gere QR codes para mesas e gerencie cardápios digitais em tempo real.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function loadIngredientesPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Gestão de Ingredientes</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="openIngredienteModal()">
                        <i class="fas fa-plus"></i> Novo Ingrediente
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div class="form-group">
                    <input type="text" class="form-control" id="searchIngredientes" 
                           placeholder="Buscar ingrediente...">
                </div>
                <div id="ingredientesTable"></div>
            </div>
        </div>
    `;
    loadIngredientes();
}

function loadFichasPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Fichas Técnicas</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="openFichaModal()">
                        <i class="fas fa-plus"></i> Nova Ficha Técnica
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div id="fichasTable"></div>
            </div>
        </div>
    `;
    loadFichas();
}

function loadInventarioPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Inventário</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="gerarInventario()">
                        <i class="fas fa-plus"></i> Gerar Inventário
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div id="inventarioContent"></div>
            </div>
        </div>
    `;
    loadInventario();
}

function loadCardapioPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Cardápios</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="openCardapioModal()">
                        <i class="fas fa-plus"></i> Novo Cardápio
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div id="cardapiosTable"></div>
            </div>
        </div>
    `;
    loadCardapios();
}

function loadMesasPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Mesas & QR Codes</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="openMesaModal()">
                        <i class="fas fa-plus"></i> Nova Mesa
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div id="mesasTable"></div>
            </div>
        </div>
    `;
    loadMesas();
}

function loadVendasPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Vendas</h2>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="openVendaModal()">
                        <i class="fas fa-plus"></i> Registrar Venda
                    </button>
                </div>
            </div>
            <div class="section-body">
                <div id="vendasTable"></div>
            </div>
        </div>
    `;
    loadVendas();
}

function loadRelatoriosPage() {
    contentArea.innerHTML = `
        <div class="content-section">
            <div class="section-header">
                <h2 class="section-title">Relatórios</h2>
            </div>
            <div class="section-body">
                <div class="row">
                    <div class="col-6">
                        <div class="card">
                            <h3><i class="fas fa-chart-bar"></i> Relatório de Vendas</h3>
                            <p>Análise detalhada de vendas por período</p>
                            <button class="btn btn-primary mt-2" onclick="gerarRelatorioVendas()">
                                Gerar Relatório
                            </button>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card">
                            <h3><i class="fas fa-warehouse"></i> Relatório de Estoque</h3>
                            <p>Situação atual do estoque e valores</p>
                            <button class="btn btn-primary mt-2" onclick="gerarRelatorioEstoque()">
                                Gerar Relatório
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ========== FUNÇÕES DE CARREGAMENTO DE DADOS ==========
async function loadIngredientes() {
    try {
        const ingredientes = await API.Ingredientes.list();
        const table = document.getElementById('ingredientesTable');
        
        if (ingredientes.length === 0) {
            table.innerHTML = '<p class="text-center">Nenhum ingrediente cadastrado</p>';
            return;
        }
        
        let html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Unidade</th>
                        <th>Custo Unitário</th>
                        <th>Estoque Atual</th>
                        <th>Estoque Mínimo</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        ingredientes.forEach(ing => {
            const statusBadge = ing.estoque_atual <= ing.estoque_minimo 
                ? '<span class="badge badge-danger">Baixo</span>'
                : '<span class="badge badge-success">OK</span>';
            
            html += `
                <tr>
                    <td>${ing.nome}</td>
                    <td>${ing.unidade_medida}</td>
                    <td>${Utils.formatCurrency(ing.custo_unitario)}</td>
                    <td>${ing.estoque_atual} ${statusBadge}</td>
                    <td>${ing.estoque_minimo}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editIngrediente(${ing.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteIngrediente(${ing.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        table.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar ingredientes:', error);
        Utils.showAlert('Erro ao carregar ingredientes', 'danger');
    }
}

async function loadFichas() {
    try {
        const fichas = await API.Fichas.list();
        const table = document.getElementById('fichasTable');
        
        if (fichas.length === 0) {
            table.innerHTML = '<p class="text-center">Nenhuma ficha técnica cadastrada</p>';
            return;
        }
        
        let html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Prato</th>
                        <th>Categoria</th>
                        <th>Porções</th>
                        <th>Custo Total</th>
                        <th>Preço Venda</th>
                        <th>Margem</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        fichas.forEach(ficha => {
            html += `
                <tr>
                    <td>${ficha.nome_prato}</td>
                    <td>${ficha.categoria || '-'}</td>
                    <td>${ficha.porcoes}</td>
                    <td>${Utils.formatCurrency(ficha.custo_total)}</td>
                    <td>${Utils.formatCurrency(ficha.preco_venda)}</td>
                    <td>${ficha.margem_lucro.toFixed(1)}%</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewFicha(${ficha.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteFicha(${ficha.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        table.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar fichas:', error);
        Utils.showAlert('Erro ao carregar fichas técnicas', 'danger');
    }
}

async function loadInventario() {
    // Implementação simplificada
    document.getElementById('inventarioContent').innerHTML = `
        <p>Funcionalidade de inventário será implementada nas próximas páginas específicas.</p>
    `;
}

async function loadCardapios() {
    // Implementação simplificada
    document.getElementById('cardapiosTable').innerHTML = `
        <p>Funcionalidade de cardápios será implementada nas próximas páginas específicas.</p>
    `;
}

async function loadMesas() {
    // Implementação simplificada
    document.getElementById('mesasTable').innerHTML = `
        <p>Funcionalidade de mesas será implementada nas próximas páginas específicas.</p>
    `;
}

async function loadVendas() {
    // Implementação simplificada
    document.getElementById('vendasTable').innerHTML = `
        <p>Funcionalidade de vendas será implementada nas próximas páginas específicas.</p>
    `;
}

// ========== FUNÇÕES AUXILIARES (PLACEHOLDERS) ==========
function openIngredienteModal() {
    Utils.showAlert('Modal de ingrediente será implementado', 'info');
}

function editIngrediente(id) {
    Utils.showAlert(`Editar ingrediente ${id}`, 'info');
}

function deleteIngrediente(id) {
    if (confirm('Deseja realmente excluir este ingrediente?')) {
        API.Ingredientes.delete(id)
            .then(() => {
                Utils.showAlert('Ingrediente excluído com sucesso', 'success');
                loadIngredientes();
            })
            .catch(error => {
                Utils.showAlert('Erro ao excluir ingrediente', 'danger');
            });
    }
}

function openFichaModal() {
    Utils.showAlert('Modal de ficha técnica será implementado', 'info');
}

function viewFicha(id) {
    Utils.showAlert(`Visualizar ficha ${id}`, 'info');
}

function deleteFicha(id) {
    if (confirm('Deseja realmente excluir esta ficha técnica?')) {
        API.Fichas.delete(id)
            .then(() => {
                Utils.showAlert('Ficha técnica excluída com sucesso', 'success');
                loadFichas();
            })
            .catch(error => {
                Utils.showAlert('Erro ao excluir ficha técnica', 'danger');
            });
    }
}

function gerarInventario() {
    Utils.showAlert('Gerar inventário será implementado', 'info');
}

function openCardapioModal() {
    Utils.showAlert('Modal de cardápio será implementado', 'info');
}

function openMesaModal() {
    Utils.showAlert('Modal de mesa será implementado', 'info');
}

function openVendaModal() {
    Utils.showAlert('Modal de venda será implementado', 'info');
}

function gerarRelatorioVendas() {
    Utils.showAlert('Relatório de vendas será implementado', 'info');
}

function gerarRelatorioEstoque() {
    Utils.showAlert('Relatório de estoque será implementado', 'info');
}
