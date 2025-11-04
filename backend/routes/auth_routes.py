from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import hash_password, check_password, generate_token, token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    data = request.get_json()
    
    # Validar dados
    if not data or not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400
    
    nome = data['nome']
    email = data['email']
    senha = data['senha']
    perfil = data.get('perfil', 'usuario')
    
    # Hash da senha
    senha_hash = hash_password(senha)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se email já existe
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
            if cursor.fetchone():
                return jsonify({'error': 'Email já cadastrado'}), 400
            
            # Inserir usuário
            cursor.execute('''
                INSERT INTO usuarios (nome, email, senha_hash, perfil)
                VALUES (?, ?, ?, ?)
            ''', (nome, email, senha_hash, perfil))
            
            user_id = cursor.lastrowid
            
            # Gerar token
            token = generate_token(user_id, email, perfil)
            
            return jsonify({
                'message': 'Usuário registrado com sucesso',
                'token': token,
                'user': {
                    'id': user_id,
                    'nome': nome,
                    'email': email,
                    'perfil': perfil
                }
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Realiza login do usuário"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    email = data['email']
    senha = data['senha']
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute('''
                SELECT id, nome, email, senha_hash, perfil, ativo
                FROM usuarios
                WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Email ou senha inválidos'}), 401
            
            if not user['ativo']:
                return jsonify({'error': 'Usuário inativo'}), 401
            
            # Verificar senha
            if not check_password(senha, user['senha_hash']):
                return jsonify({'error': 'Email ou senha inválidos'}), 401
            
            # Gerar token
            token = generate_token(user['id'], user['email'], user['perfil'])
            
            return jsonify({
                'message': 'Login realizado com sucesso',
                'token': token,
                'user': {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil']
                }
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Retorna informações do usuário autenticado"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nome, email, perfil, criado_em
                FROM usuarios
                WHERE id = ? AND ativo = 1
            ''', (request.user['user_id'],))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            return jsonify({
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'perfil': user['perfil'],
                'criado_em': user['criado_em']
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Altera a senha do usuário"""
    data = request.get_json()
    
    if not data or not data.get('senha_atual') or not data.get('senha_nova'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    senha_atual = data['senha_atual']
    senha_nova = data['senha_nova']
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar senha atual
            cursor.execute('SELECT senha_hash FROM usuarios WHERE id = ?', 
                         (request.user['user_id'],))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            # Verificar senha atual
            if not check_password(senha_atual, user['senha_hash']):
                return jsonify({'error': 'Senha atual incorreta'}), 401
            
            # Atualizar senha
            nova_senha_hash = hash_password(senha_nova)
            cursor.execute('''
                UPDATE usuarios 
                SET senha_hash = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (nova_senha_hash, request.user['user_id']))
            
            return jsonify({'message': 'Senha alterada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
