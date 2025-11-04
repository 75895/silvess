from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import token_required
from utils.qrcode_generator import generate_menu_qrcode
import os

cardapio_bp = Blueprint('cardapio', __name__)

# ========== CARDÁPIOS ==========

@cardapio_bp.route('/', methods=['GET'])
def list_cardapios():
    """Lista todos os cardápios (público para visualização)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            ativo = request.args.get('ativo')
            data = request.args.get('data')
            
            query = 'SELECT * FROM cardapios WHERE 1=1'
            params = []
            
            if ativo is not None:
                query += ' AND ativo = ?'
                params.append(ativo)
            
            if data:
                query += ' AND data = ?'
                params.append(data)
            
            query += ' ORDER BY data DESC, criado_em DESC'
            
            cursor.execute(query, params)
            cardapios = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(cardapios), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/<int:id>', methods=['GET'])
def get_cardapio(id):
    """Busca um cardápio com seus pratos (público)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar cardápio
            cursor.execute('SELECT * FROM cardapios WHERE id = ?', (id,))
            cardapio = cursor.fetchone()
            
            if not cardapio:
                return jsonify({'error': 'Cardápio não encontrado'}), 404
            
            cardapio_dict = dict(cardapio)
            
            # Buscar pratos do cardápio
            cursor.execute('''
                SELECT 
                    cp.id,
                    cp.disponivel,
                    cp.ordem,
                    ft.id as ficha_id,
                    ft.nome_prato,
                    ft.descricao,
                    ft.categoria,
                    ft.preco_venda,
                    ft.tempo_preparo,
                    ft.porcoes
                FROM cardapio_pratos cp
                JOIN fichas_tecnicas ft ON cp.ficha_tecnica_id = ft.id
                WHERE cp.cardapio_id = ?
                ORDER BY cp.ordem, ft.categoria, ft.nome_prato
            ''', (id,))
            
            pratos = [dict(row) for row in cursor.fetchall()]
            cardapio_dict['pratos'] = pratos
            
            return jsonify(cardapio_dict), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/', methods=['POST'])
@token_required
def create_cardapio():
    """Cria um novo cardápio"""
    data = request.get_json()
    
    if not data.get('nome') or not data.get('data'):
        return jsonify({'error': 'Nome e data são obrigatórios'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Inserir cardápio
            cursor.execute('''
                INSERT INTO cardapios (data, nome, descricao, ativo)
                VALUES (?, ?, ?, ?)
            ''', (
                data['data'],
                data['nome'],
                data.get('descricao', ''),
                data.get('ativo', 1)
            ))
            
            cardapio_id = cursor.lastrowid
            
            # Adicionar pratos se fornecidos
            if data.get('pratos'):
                for idx, prato in enumerate(data['pratos']):
                    cursor.execute('''
                        INSERT INTO cardapio_pratos
                        (cardapio_id, ficha_tecnica_id, disponivel, ordem)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        cardapio_id,
                        prato['ficha_tecnica_id'],
                        prato.get('disponivel', 1),
                        prato.get('ordem', idx)
                    ))
            
            return jsonify({
                'message': 'Cardápio criado com sucesso',
                'id': cardapio_id
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_cardapio(id):
    """Atualiza um cardápio"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se existe
            cursor.execute('SELECT id FROM cardapios WHERE id = ?', (id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Cardápio não encontrado'}), 404
            
            # Atualizar cardápio
            cursor.execute('''
                UPDATE cardapios
                SET nome = ?, descricao = ?, data = ?, ativo = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('nome'),
                data.get('descricao'),
                data.get('data'),
                data.get('ativo'),
                id
            ))
            
            # Se pratos foram enviados, atualizar
            if 'pratos' in data:
                # Remover pratos antigos
                cursor.execute('DELETE FROM cardapio_pratos WHERE cardapio_id = ?', (id,))
                
                # Adicionar novos pratos
                for idx, prato in enumerate(data['pratos']):
                    cursor.execute('''
                        INSERT INTO cardapio_pratos
                        (cardapio_id, ficha_tecnica_id, disponivel, ordem)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        id,
                        prato['ficha_tecnica_id'],
                        prato.get('disponivel', 1),
                        prato.get('ordem', idx)
                    ))
            
            return jsonify({'message': 'Cardápio atualizado com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_cardapio(id):
    """Desativa um cardápio"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM cardapios WHERE id = ?', (id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Cardápio não encontrado'}), 404
            
            cursor.execute('''
                UPDATE cardapios
                SET ativo = 0, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (id,))
            
            return jsonify({'message': 'Cardápio desativado com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/<int:cardapio_id>/prato/<int:prato_id>/disponibilidade', methods=['PUT'])
@token_required
def toggle_prato_disponibilidade(cardapio_id, prato_id):
    """Alterna a disponibilidade de um prato no cardápio"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cardapio_pratos
                SET disponivel = ?
                WHERE id = ? AND cardapio_id = ?
            ''', (
                data.get('disponivel', 1),
                prato_id,
                cardapio_id
            ))
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'Prato não encontrado no cardápio'}), 404
            
            return jsonify({'message': 'Disponibilidade atualizada com sucesso'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== MESAS ==========

@cardapio_bp.route('/mesas', methods=['GET'])
@token_required
def list_mesas():
    """Lista todas as mesas"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    m.*,
                    c.nome as cardapio_nome,
                    c.data as cardapio_data
                FROM mesas m
                LEFT JOIN cardapios c ON m.cardapio_id = c.id
                WHERE m.ativo = 1
                ORDER BY m.numero
            ''')
            
            mesas = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(mesas), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/mesas', methods=['POST'])
@token_required
def create_mesa():
    """Cria uma nova mesa"""
    data = request.get_json()
    
    if not data.get('numero'):
        return jsonify({'error': 'Número da mesa é obrigatório'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se número já existe
            cursor.execute('SELECT id FROM mesas WHERE numero = ?', (data['numero'],))
            if cursor.fetchone():
                return jsonify({'error': 'Número de mesa já existe'}), 400
            
            # Inserir mesa
            cursor.execute('''
                INSERT INTO mesas (numero, cardapio_id, ativo)
                VALUES (?, ?, ?)
            ''', (
                data['numero'],
                data.get('cardapio_id'),
                data.get('ativo', 1)
            ))
            
            mesa_id = cursor.lastrowid
            
            # Gerar QR code se cardápio foi definido
            qrcode_url = None
            if data.get('cardapio_id'):
                base_url = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
                qrcode_url = generate_menu_qrcode(
                    data['numero'],
                    data['cardapio_id'],
                    base_url
                )
                
                # Atualizar mesa com QR code
                cursor.execute('''
                    UPDATE mesas SET qrcode_url = ? WHERE id = ?
                ''', (qrcode_url, mesa_id))
            
            return jsonify({
                'message': 'Mesa criada com sucesso',
                'id': mesa_id,
                'qrcode_url': qrcode_url
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/mesas/<int:id>', methods=['PUT'])
@token_required
def update_mesa(id):
    """Atualiza uma mesa e seu cardápio"""
    data = request.get_json()
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar mesa atual
            cursor.execute('SELECT * FROM mesas WHERE id = ?', (id,))
            mesa = cursor.fetchone()
            
            if not mesa:
                return jsonify({'error': 'Mesa não encontrada'}), 404
            
            # Atualizar mesa
            novo_cardapio_id = data.get('cardapio_id', mesa['cardapio_id'])
            
            cursor.execute('''
                UPDATE mesas
                SET cardapio_id = ?, ativo = ?
                WHERE id = ?
            ''', (
                novo_cardapio_id,
                data.get('ativo', mesa['ativo']),
                id
            ))
            
            # Regenerar QR code se cardápio mudou
            qrcode_url = mesa['qrcode_url']
            if novo_cardapio_id and novo_cardapio_id != mesa['cardapio_id']:
                base_url = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
                qrcode_url = generate_menu_qrcode(
                    mesa['numero'],
                    novo_cardapio_id,
                    base_url
                )
                
                cursor.execute('''
                    UPDATE mesas SET qrcode_url = ? WHERE id = ?
                ''', (qrcode_url, id))
            
            return jsonify({
                'message': 'Mesa atualizada com sucesso',
                'qrcode_url': qrcode_url
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cardapio_bp.route('/mesas/<int:id>/qrcode', methods=['GET'])
@token_required
def get_mesa_qrcode(id):
    """Obtém o QR code de uma mesa"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT numero, cardapio_id, qrcode_url FROM mesas WHERE id = ?', (id,))
            mesa = cursor.fetchone()
            
            if not mesa:
                return jsonify({'error': 'Mesa não encontrada'}), 404
            
            if not mesa['cardapio_id']:
                return jsonify({'error': 'Mesa não possui cardápio associado'}), 400
            
            # Se não tem QR code, gerar
            qrcode_url = mesa['qrcode_url']
            if not qrcode_url:
                base_url = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
                qrcode_url = generate_menu_qrcode(
                    mesa['numero'],
                    mesa['cardapio_id'],
                    base_url
                )
                
                cursor.execute('''
                    UPDATE mesas SET qrcode_url = ? WHERE id = ?
                ''', (qrcode_url, id))
            
            return jsonify({
                'mesa_numero': mesa['numero'],
                'cardapio_id': mesa['cardapio_id'],
                'qrcode_url': qrcode_url
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
