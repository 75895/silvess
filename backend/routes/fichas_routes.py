from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import token_required

fichas_bp = Blueprint('fichas', __name__)

@fichas_bp.route('/', methods=['GET'])
@token_required
def list_fichas():
    """Lista todas as fichas técnicas"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            ativo = request.args.get('ativo', '1')
            categoria = request.args.get('categoria', '')
            search = request.args.get('search', '')
            
            query = 'SELECT * FROM fichas_tecnicas WHERE ativo = ?'
            params = [ativo]
            
            if categoria:
                query += ' AND categoria = ?'
                params.append(categoria)
            
            if search:
                query += ' AND nome_prato LIKE ?'
                params.append(f'%{search}%')
            
            query += ' ORDER BY nome_prato'
            
            cursor.execute(query, params)
            fichas = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(fichas), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_ficha(id):
    """Busca uma ficha técnica por ID com seus ingredientes"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar ficha
            cursor.execute('SELECT * FROM fichas_tecnicas WHERE id = ?', (id,))
            ficha = cursor.fetchone()
            
            if not ficha:
                return jsonify({'error': 'Ficha técnica não encontrada'}), 404
            
            ficha_dict = dict(ficha)
            
            # Buscar ingredientes da ficha
            cursor.execute('''
                SELECT 
                    fi.id,
                    fi.quantidade_gramas,
                    fi.custo_parcial,
                    i.id as ingrediente_id,
                    i.nome as ingrediente_nome,
                    i.unidade_medida,
                    i.custo_unitario
                FROM ficha_ingredientes fi
                JOIN ingredientes i ON fi.ingrediente_id = i.id
                WHERE fi.ficha_id = ?
                ORDER BY i.nome
            ''', (id,))
            
            ingredientes = [dict(row) for row in cursor.fetchall()]
            ficha_dict['ingredientes'] = ingredientes
            
            return jsonify(ficha_dict), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas_bp.route('/', methods=['POST'])
@token_required
def create_ficha():
    """Cria uma nova ficha técnica"""
    data = request.get_json()
    
    # Validar dados obrigatórios
    if not data.get('nome_prato'):
        return jsonify({'error': 'Nome do prato é obrigatório'}), 400
    
    if not data.get('ingredientes') or len(data['ingredientes']) == 0:
        return jsonify({'error': 'Adicione pelo menos um ingrediente'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Calcular custo total
            custo_total = 0
            ingredientes_validados = []
            
            for ing in data['ingredientes']:
                if not ing.get('ingrediente_id') or not ing.get('quantidade_gramas'):
                    return jsonify({'error': 'Ingrediente e quantidade são obrigatórios'}), 400
                
                # Buscar custo do ingrediente
                cursor.execute('''
                    SELECT custo_unitario, unidade_medida 
                    FROM ingredientes 
                    WHERE id = ?
                ''', (ing['ingrediente_id'],))
                
                ingrediente = cursor.fetchone()
                if not ingrediente:
                    return jsonify({'error': f'Ingrediente {ing["ingrediente_id"]} não encontrado'}), 404
                
                # Calcular custo parcial (convertendo gramas para a unidade do ingrediente)
                quantidade_gramas = float(ing['quantidade_gramas'])
                
                # Assumindo que custo_unitario é por kg
                custo_parcial = (quantidade_gramas / 1000) * ingrediente['custo_unitario']
                
                custo_total += custo_parcial
                ingredientes_validados.append({
                    'ingrediente_id': ing['ingrediente_id'],
                    'quantidade_gramas': quantidade_gramas,
                    'custo_parcial': custo_parcial
                })
            
            # Calcular margem de lucro se preço de venda foi informado
            preco_venda = float(data.get('preco_venda', 0))
            margem_lucro = 0
            if preco_venda > 0 and custo_total > 0:
                margem_lucro = ((preco_venda - custo_total) / custo_total) * 100
            
            # Inserir ficha técnica
            cursor.execute('''
                INSERT INTO fichas_tecnicas
                (nome_prato, categoria, descricao, porcoes, tempo_preparo, 
                 modo_preparo, validade_horas, custo_total, preco_venda, margem_lucro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['nome_prato'],
                data.get('categoria', ''),
                data.get('descricao', ''),
                data.get('porcoes', 1),
                data.get('tempo_preparo', 0),
                data.get('modo_preparo', ''),
                data.get('validade_horas', 0),
                custo_total,
                preco_venda,
                margem_lucro
            ))
            
            ficha_id = cursor.lastrowid
            
            # Inserir ingredientes da ficha
            for ing in ingredientes_validados:
                cursor.execute('''
                    INSERT INTO ficha_ingredientes
                    (ficha_id, ingrediente_id, quantidade_gramas, custo_parcial)
                    VALUES (?, ?, ?, ?)
                ''', (
                    ficha_id,
                    ing['ingrediente_id'],
                    ing['quantidade_gramas'],
                    ing['custo_parcial']
                ))
            
            return jsonify({
                'message': 'Ficha técnica criada com sucesso',
                'id': ficha_id,
                'custo_total': custo_total,
                'margem_lucro': margem_lucro
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_ficha(id):
    """Atualiza uma ficha técnica"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se existe
            cursor.execute('SELECT id FROM fichas_tecnicas WHERE id = ?', (id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Ficha técnica não encontrada'}), 404
            
            # Se ingredientes foram enviados, recalcular custos
            if data.get('ingredientes'):
                # Remover ingredientes antigos
                cursor.execute('DELETE FROM ficha_ingredientes WHERE ficha_id = ?', (id,))
                
                # Calcular novo custo
                custo_total = 0
                for ing in data['ingredientes']:
                    cursor.execute('''
                        SELECT custo_unitario FROM ingredientes WHERE id = ?
                    ''', (ing['ingrediente_id'],))
                    
                    ingrediente = cursor.fetchone()
                    if not ingrediente:
                        continue
                    
                    quantidade_gramas = float(ing['quantidade_gramas'])
                    custo_parcial = (quantidade_gramas / 1000) * ingrediente['custo_unitario']
                    custo_total += custo_parcial
                    
                    # Inserir novo ingrediente
                    cursor.execute('''
                        INSERT INTO ficha_ingredientes
                        (ficha_id, ingrediente_id, quantidade_gramas, custo_parcial)
                        VALUES (?, ?, ?, ?)
                    ''', (id, ing['ingrediente_id'], quantidade_gramas, custo_parcial))
                
                data['custo_total'] = custo_total
            
            # Recalcular margem se necessário
            if data.get('preco_venda') and data.get('custo_total'):
                preco_venda = float(data['preco_venda'])
                custo_total = float(data['custo_total'])
                if custo_total > 0:
                    data['margem_lucro'] = ((preco_venda - custo_total) / custo_total) * 100
            
            # Atualizar ficha
            cursor.execute('''
                UPDATE fichas_tecnicas
                SET nome_prato = ?, categoria = ?, descricao = ?, porcoes = ?,
                    tempo_preparo = ?, modo_preparo = ?, validade_horas = ?,
                    custo_total = ?, preco_venda = ?, margem_lucro = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('nome_prato'),
                data.get('categoria'),
                data.get('descricao'),
                data.get('porcoes'),
                data.get('tempo_preparo'),
                data.get('modo_preparo'),
                data.get('validade_horas'),
                data.get('custo_total'),
                data.get('preco_venda'),
                data.get('margem_lucro', 0),
                id
            ))
            
            return jsonify({'message': 'Ficha técnica atualizada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_ficha(id):
    """Desativa uma ficha técnica"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM fichas_tecnicas WHERE id = ?', (id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Ficha técnica não encontrada'}), 404
            
            cursor.execute('''
                UPDATE fichas_tecnicas
                SET ativo = 0, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (id,))
            
            return jsonify({'message': 'Ficha técnica desativada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas_bp.route('/categorias', methods=['GET'])
@token_required
def get_categorias():
    """Lista todas as categorias de fichas técnicas"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT categoria 
                FROM fichas_tecnicas 
                WHERE ativo = 1 AND categoria IS NOT NULL AND categoria != ''
                ORDER BY categoria
            ''')
            
            categorias = [row['categoria'] for row in cursor.fetchall()]
            
            return jsonify(categorias), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
