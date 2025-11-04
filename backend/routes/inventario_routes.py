from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import token_required
from datetime import datetime

inventario_bp = Blueprint('inventario', __name__)

@inventario_bp.route('/', methods=['GET'])
@token_required
def list_inventarios():
    """Lista inventários com filtros"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            ingrediente_id = request.args.get('ingrediente_id')
            
            query = '''
                SELECT 
                    inv.*,
                    ing.nome as ingrediente_nome,
                    ing.unidade_medida,
                    u.nome as usuario_nome
                FROM inventario inv
                JOIN ingredientes ing ON inv.ingrediente_id = ing.id
                LEFT JOIN usuarios u ON inv.usuario_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if data_inicio:
                query += ' AND inv.data_inventario >= ?'
                params.append(data_inicio)
            
            if data_fim:
                query += ' AND inv.data_inventario <= ?'
                params.append(data_fim)
            
            if ingrediente_id:
                query += ' AND inv.ingrediente_id = ?'
                params.append(ingrediente_id)
            
            query += ' ORDER BY inv.data_inventario DESC, ing.nome'
            
            cursor.execute(query, params)
            inventarios = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(inventarios), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/gerar', methods=['POST'])
@token_required
def gerar_inventario():
    """Gera um novo inventário com base no estoque atual"""
    data = request.get_json()
    
    data_inventario = data.get('data_inventario', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar todos os ingredientes ativos
            cursor.execute('''
                SELECT id, nome, estoque_atual
                FROM ingredientes
                WHERE ativo = 1
                ORDER BY nome
            ''')
            
            ingredientes = cursor.fetchall()
            
            if not ingredientes:
                return jsonify({'error': 'Nenhum ingrediente ativo encontrado'}), 404
            
            inventarios_criados = []
            
            for ingrediente in ingredientes:
                # Verificar se já existe inventário para este ingrediente nesta data
                cursor.execute('''
                    SELECT id FROM inventario
                    WHERE ingrediente_id = ? AND data_inventario = ?
                ''', (ingrediente['id'], data_inventario))
                
                if cursor.fetchone():
                    continue  # Já existe, pular
                
                # Criar registro de inventário
                cursor.execute('''
                    INSERT INTO inventario
                    (data_inventario, ingrediente_id, quantidade_sistema, 
                     quantidade_fisica, diferenca, editavel, usuario_id)
                    VALUES (?, ?, ?, NULL, NULL, 1, ?)
                ''', (
                    data_inventario,
                    ingrediente['id'],
                    ingrediente['estoque_atual'],
                    request.user['user_id']
                ))
                
                inventarios_criados.append({
                    'id': cursor.lastrowid,
                    'ingrediente_id': ingrediente['id'],
                    'ingrediente_nome': ingrediente['nome'],
                    'quantidade_sistema': ingrediente['estoque_atual']
                })
            
            return jsonify({
                'message': f'Inventário gerado com sucesso',
                'data_inventario': data_inventario,
                'total_itens': len(inventarios_criados),
                'itens': inventarios_criados
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/<int:id>', methods=['PUT'])
@token_required
def atualizar_inventario(id):
    """Atualiza um item do inventário com a contagem física"""
    data = request.get_json()
    
    if 'quantidade_fisica' not in data:
        return jsonify({'error': 'quantidade_fisica é obrigatória'}), 400
    
    quantidade_fisica = float(data['quantidade_fisica'])
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar inventário
            cursor.execute('''
                SELECT * FROM inventario WHERE id = ?
            ''', (id,))
            
            inventario = cursor.fetchone()
            
            if not inventario:
                return jsonify({'error': 'Inventário não encontrado'}), 404
            
            if not inventario['editavel']:
                return jsonify({'error': 'Este inventário não é mais editável'}), 400
            
            # Calcular diferença
            quantidade_sistema = inventario['quantidade_sistema']
            diferenca = quantidade_fisica - quantidade_sistema
            
            # Atualizar inventário
            cursor.execute('''
                UPDATE inventario
                SET quantidade_fisica = ?,
                    diferenca = ?,
                    observacoes = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                quantidade_fisica,
                diferenca,
                data.get('observacoes', inventario['observacoes']),
                id
            ))
            
            # Se houver diferença, perguntar se deve ajustar o estoque
            ajustar_estoque = data.get('ajustar_estoque', False)
            
            if ajustar_estoque and diferenca != 0:
                # Atualizar estoque do ingrediente
                cursor.execute('''
                    UPDATE ingredientes
                    SET estoque_atual = ?,
                        atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantidade_fisica, inventario['ingrediente_id']))
                
                # Registrar movimentação
                tipo_mov = 'entrada' if diferenca > 0 else 'saida'
                quantidade_mov = abs(diferenca)
                
                cursor.execute('''
                    INSERT INTO movimentacoes_estoque
                    (ingrediente_id, tipo, quantidade, usuario_id, observacao)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    inventario['ingrediente_id'],
                    tipo_mov,
                    quantidade_mov,
                    request.user['user_id'],
                    f'Ajuste de inventário - {data.get("observacoes", "")}'
                ))
            
            return jsonify({
                'message': 'Inventário atualizado com sucesso',
                'quantidade_sistema': quantidade_sistema,
                'quantidade_fisica': quantidade_fisica,
                'diferenca': diferenca,
                'estoque_ajustado': ajustar_estoque
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/fechar/<data_inventario>', methods=['POST'])
@token_required
def fechar_inventario(data_inventario):
    """Fecha o inventário de uma data, tornando-o não editável"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verificar se há itens pendentes (sem contagem física)
            cursor.execute('''
                SELECT COUNT(*) as pendentes
                FROM inventario
                WHERE data_inventario = ? AND quantidade_fisica IS NULL
            ''', (data_inventario,))
            
            resultado = cursor.fetchone()
            pendentes = resultado['pendentes']
            
            if pendentes > 0:
                return jsonify({
                    'error': f'Há {pendentes} itens sem contagem física',
                    'pendentes': pendentes
                }), 400
            
            # Marcar todos como não editáveis
            cursor.execute('''
                UPDATE inventario
                SET editavel = 0,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE data_inventario = ?
            ''', (data_inventario,))
            
            itens_fechados = cursor.rowcount
            
            return jsonify({
                'message': 'Inventário fechado com sucesso',
                'data_inventario': data_inventario,
                'itens_fechados': itens_fechados
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/relatorio/<data_inventario>', methods=['GET'])
@token_required
def relatorio_inventario(data_inventario):
    """Gera relatório do inventário de uma data"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    inv.*,
                    ing.nome as ingrediente_nome,
                    ing.unidade_medida,
                    ing.custo_unitario,
                    (inv.diferenca * ing.custo_unitario / 1000) as valor_diferenca
                FROM inventario inv
                JOIN ingredientes ing ON inv.ingrediente_id = ing.id
                WHERE inv.data_inventario = ?
                ORDER BY ABS(inv.diferenca) DESC
            ''', (data_inventario,))
            
            itens = [dict(row) for row in cursor.fetchall()]
            
            # Calcular totais
            total_itens = len(itens)
            itens_com_diferenca = sum(1 for item in itens if item['diferenca'] and item['diferenca'] != 0)
            valor_total_diferencas = sum(item['valor_diferenca'] or 0 for item in itens)
            
            return jsonify({
                'data_inventario': data_inventario,
                'total_itens': total_itens,
                'itens_com_diferenca': itens_com_diferenca,
                'valor_total_diferencas': valor_total_diferencas,
                'itens': itens
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/reabrir/<data_inventario>', methods=['POST'])
@token_required
def reabrir_inventario(data_inventario):
    """Reabre um inventário fechado para edição"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE inventario
                SET editavel = 1,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE data_inventario = ?
            ''', (data_inventario,))
            
            itens_reabertos = cursor.rowcount
            
            if itens_reabertos == 0:
                return jsonify({'error': 'Nenhum inventário encontrado para esta data'}), 404
            
            return jsonify({
                'message': 'Inventário reaberto com sucesso',
                'data_inventario': data_inventario,
                'itens_reabertos': itens_reabertos
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
