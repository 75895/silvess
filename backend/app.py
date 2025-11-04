from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Importar rotas
from routes.auth_routes import auth_bp
from routes.ingredientes_routes import ingredientes_bp
from routes.fichas_routes import fichas_bp
from routes.inventario_routes import inventario_bp
from routes.cardapio_routes import cardapio_bp
from routes.dashboard_routes import dashboard_bp

# Importar database
from models.database import init_db

# Criar aplicação Flask
app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'silvess-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Habilitar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ingredientes_bp, url_prefix='/api/ingredientes')
app.register_blueprint(fichas_bp, url_prefix='/api/fichas')
app.register_blueprint(inventario_bp, url_prefix='/api/inventario')
app.register_blueprint(cardapio_bp, url_prefix='/api/cardapio')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# Rota raiz
@app.route('/')
def index():
    return jsonify({
        'message': 'SILVESS API - Sistema de Gestão de Restaurantes',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'ingredientes': '/api/ingredientes',
            'fichas_tecnicas': '/api/fichas',
            'inventario': '/api/inventario',
            'cardapio': '/api/cardapio',
            'dashboard': '/api/dashboard'
        }
    })

# Rota de health check
@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

# Handler de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Inicializar banco de dados
with app.app_context():
    init_db()
    print("✓ Banco de dados inicializado")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"🍽️  SILVESS API Server")
    print(f"{'='*50}")
    print(f"📍 Rodando em: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
