from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import token_required

ingredientes_bp = Blueprint('ingredientes', __name__)

@ingredientes_bp.route('/', methods=['GET'])
@token_required
def list_ingredientes():
    """Lista todos os ingredientes"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Filtros opcionais
            ativo = request.args.get('ativo', '1')
            search = request.args.get('search', '')
            
            query = 'SELECT * FROM ingredientes WHERE ativo = ?'
            params = [ativo]
            
            if search:
                query += ' AND nome LIKE ?'
                params.append(f'%{search}%')
            
            query += ' ORDER BY nome'
            
            cursor.execute(query, params)
            ingredientes = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(ingredientes), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_ingrediente(id):
    """Busca um ingrediente por ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM ingredientes WHERE id = ?', (id,))
            ingrediente = cursor.fetchone()
            
            if not ingrediente:
                return jsonify({'error': 'Ingrediente não encontrado'}), 404
            
            return jsonify(dict(ingrediente)), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/', methods=['POST'])
@token_required
def create_ingrediente():
    """Cria um novo ingrediente"""
    data = request.get_json()
    
    # Validar dados obrigatórios
    required_fields = ['nome', 'unidade_medida', 'custo_unitario']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ingredientes 
                (nome, unidade_medida, custo_unitario, estoque_atual, estoque_minimo, fornecedor)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['nome'],
                data['unidade_medida'],
                data['custo_unitario'],
                data.get('estoque_atual', 0),
                data.get('estoque_minimo', 0),
                data.get('fornecedor', '')
            ))
            
            ingrediente_id = cursor.lastrowid
            
            # Registrar movimentação inicial se houver estoque
            if data.get('estoque_atual', 0) > 0:
                cursor.execute('''
                    INSERT INTO movimentacoes_estoque
                    (ingrediente_id, tipo, quantidade, usuario_id, observacao)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    ingrediente_id,
                    'entrada',
                    data.get('estoque_atual', 0),
                    request.user['user_id'],
                    'Estoque inicial'
                ))
            
            return jsonify({
                'message': 'Ingrediente criado com sucesso',
                'id': ingrediente_id
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_ingrediente(id):
    """Atualiza um ingrediente"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se existe
            cursor.execute('SELECT * FROM ingredientes WHERE id = ?', (id,))
            ingrediente_atual = cursor.fetchone()
            
            if not ingrediente_atual:
                return jsonify({'error': 'Ingrediente não encontrado'}), 404
            
            # Atualizar campos
            cursor.execute('''
                UPDATE ingredientes
                SET nome = ?, unidade_medida = ?, custo_unitario = ?,
                    estoque_minimo = ?, fornecedor = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('nome', ingrediente_atual['nome']),
                data.get('unidade_medida', ingrediente_atual['unidade_medida']),
                data.get('custo_unitario', ingrediente_atual['custo_unitario']),
                data.get('estoque_minimo', ingrediente_atual['estoque_minimo']),
                data.get('fornecedor', ingrediente_atual['fornecedor']),
                id
            ))
            
            return jsonify({'message': 'Ingrediente atualizado com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_ingrediente(id):
    """Desativa um ingrediente (soft delete)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM ingredientes WHERE id = ?', (id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Ingrediente não encontrado'}), 404
            
            cursor.execute('''
                UPDATE ingredientes
                SET ativo = 0, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (id,))
            
            return jsonify({'message': 'Ingrediente desativado com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/<int:id>/estoque', methods=['POST'])
@token_required
def atualizar_estoque(id):
    """Atualiza o estoque de um ingrediente"""
    data = request.get_json()
    
    if not data.get('tipo') or not data.get('quantidade'):
        return jsonify({'error': 'Tipo e quantidade são obrigatórios'}), 400
    
    tipo = data['tipo']  # 'entrada' ou 'saida'
    quantidade = float(data['quantidade'])
    
    if tipo not in ['entrada', 'saida']:
        return jsonify({'error': 'Tipo deve ser entrada ou saida'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar estoque atual
            cursor.execute('SELECT estoque_atual FROM ingredientes WHERE id = ?', (id,))
            ingrediente = cursor.fetchone()
            
            if not ingrediente:
                return jsonify({'error': 'Ingrediente não encontrado'}), 404
            
            estoque_atual = ingrediente['estoque_atual']
            
            # Calcular novo estoque
            if tipo == 'entrada':
                novo_estoque = estoque_atual + quantidade
            else:
                novo_estoque = estoque_atual - quantidade
                if novo_estoque < 0:
                    return jsonify({'error': 'Estoque insuficiente'}), 400
            
            # Atualizar estoque
            cursor.execute('''
                UPDATE ingredientes
                SET estoque_atual = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (novo_estoque, id))
            
            # Registrar movimentação
            cursor.execute('''
                INSERT INTO movimentacoes_estoque
                (ingrediente_id, tipo, quantidade, usuario_id, observacao)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                id,
                tipo,
                quantidade,
                request.user['user_id'],
                data.get('observacao', '')
            ))
            
            return jsonify({
                'message': 'Estoque atualizado com sucesso',
                'estoque_anterior': estoque_atual,
                'estoque_atual': novo_estoque
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredientes_bp.route('/estoque-baixo', methods=['GET'])
@token_required
def estoque_baixo():
    """Lista ingredientes com estoque abaixo do mínimo"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ingredientes
                WHERE ativo = 1 AND estoque_atual <= estoque_minimo
                ORDER BY estoque_atual ASC
            ''')
            
            ingredientes = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(ingredientes), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
