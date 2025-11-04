from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.auth import token_required
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """Retorna estatísticas gerais do sistema"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total de ingredientes ativos
            cursor.execute('SELECT COUNT(*) as total FROM ingredientes WHERE ativo = 1')
            total_ingredientes = cursor.fetchone()['total']
            
            # Ingredientes com estoque baixo
            cursor.execute('''
                SELECT COUNT(*) as total FROM ingredientes 
                WHERE ativo = 1 AND estoque_atual <= estoque_minimo
            ''')
            estoque_baixo = cursor.fetchone()['total']
            
            # Total de fichas técnicas ativas
            cursor.execute('SELECT COUNT(*) as total FROM fichas_tecnicas WHERE ativo = 1')
            total_fichas = cursor.fetchone()['total']
            
            # Total de mesas ativas
            cursor.execute('SELECT COUNT(*) as total FROM mesas WHERE ativo = 1')
            total_mesas = cursor.fetchone()['total']
            
            # Cardápios ativos
            cursor.execute('SELECT COUNT(*) as total FROM cardapios WHERE ativo = 1')
            total_cardapios = cursor.fetchone()['total']
            
            # Vendas do mês atual
            primeiro_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_vendas,
                    SUM(valor_total) as valor_total
                FROM vendas
                WHERE data_venda >= ?
            ''', (primeiro_dia_mes,))
            
            vendas_mes = cursor.fetchone()
            
            # Vendas de hoje
            hoje = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_vendas,
                    SUM(valor_total) as valor_total
                FROM vendas
                WHERE DATE(data_venda) = ?
            ''', (hoje,))
            
            vendas_hoje = cursor.fetchone()
            
            return jsonify({
                'ingredientes': {
                    'total': total_ingredientes,
                    'estoque_baixo': estoque_baixo
                },
                'fichas_tecnicas': {
                    'total': total_fichas
                },
                'mesas': {
                    'total': total_mesas
                },
                'cardapios': {
                    'total': total_cardapios
                },
                'vendas_mes': {
                    'total': vendas_mes['total_vendas'] or 0,
                    'valor_total': vendas_mes['valor_total'] or 0
                },
                'vendas_hoje': {
                    'total': vendas_hoje['total_vendas'] or 0,
                    'valor_total': vendas_hoje['valor_total'] or 0
                }
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/vendas', methods=['GET'])
@token_required
def get_vendas():
    """Lista vendas com filtros"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            mesa_id = request.args.get('mesa_id')
            
            query = '''
                SELECT 
                    v.*,
                    ft.nome_prato,
                    m.numero as mesa_numero,
                    u.nome as usuario_nome
                FROM vendas v
                JOIN fichas_tecnicas ft ON v.ficha_tecnica_id = ft.id
                LEFT JOIN mesas m ON v.mesa_id = m.id
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if data_inicio:
                query += ' AND DATE(v.data_venda) >= ?'
                params.append(data_inicio)
            
            if data_fim:
                query += ' AND DATE(v.data_venda) <= ?'
                params.append(data_fim)
            
            if mesa_id:
                query += ' AND v.mesa_id = ?'
                params.append(mesa_id)
            
            query += ' ORDER BY v.data_venda DESC'
            
            cursor.execute(query, params)
            vendas = [dict(row) for row in cursor.fetchall()]
            
            return jsonify(vendas), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/vendas', methods=['POST'])
@token_required
def registrar_venda():
    """Registra uma nova venda"""
    data = request.get_json()
    
    if not data.get('ficha_tecnica_id') or not data.get('quantidade'):
        return jsonify({'error': 'Ficha técnica e quantidade são obrigatórios'}), 400
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Buscar preço da ficha técnica
            cursor.execute('''
                SELECT preco_venda, nome_prato FROM fichas_tecnicas WHERE id = ?
            ''', (data['ficha_tecnica_id'],))
            
            ficha = cursor.fetchone()
            if not ficha:
                return jsonify({'error': 'Ficha técnica não encontrada'}), 404
            
            valor_unitario = ficha['preco_venda']
            quantidade = int(data['quantidade'])
            valor_total = valor_unitario * quantidade
            
            # Registrar venda
            cursor.execute('''
                INSERT INTO vendas
                (mesa_id, ficha_tecnica_id, quantidade, valor_unitario, valor_total, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('mesa_id'),
                data['ficha_tecnica_id'],
                quantidade,
                valor_unitario,
                valor_total,
                request.user['user_id']
            ))
            
            venda_id = cursor.lastrowid
            
            # Baixar ingredientes do estoque
            cursor.execute('''
                SELECT ingrediente_id, quantidade_gramas
                FROM ficha_ingredientes
                WHERE ficha_id = ?
            ''', (data['ficha_tecnica_id'],))
            
            ingredientes = cursor.fetchall()
            
            for ing in ingredientes:
                quantidade_total = (ing['quantidade_gramas'] / 1000) * quantidade
                
                # Atualizar estoque
                cursor.execute('''
                    UPDATE ingredientes
                    SET estoque_atual = estoque_atual - ?,
                        atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantidade_total, ing['ingrediente_id']))
                
                # Registrar movimentação
                cursor.execute('''
                    INSERT INTO movimentacoes_estoque
                    (ingrediente_id, tipo, quantidade, usuario_id, observacao)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    ing['ingrediente_id'],
                    'saida',
                    quantidade_total,
                    request.user['user_id'],
                    f'Venda: {ficha["nome_prato"]} (x{quantidade})'
                ))
            
            return jsonify({
                'message': 'Venda registrada com sucesso',
                'id': venda_id,
                'valor_total': valor_total
            }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/relatorio/vendas', methods=['GET'])
@token_required
def relatorio_vendas():
    """Gera relatório de vendas por período"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'error': 'data_inicio e data_fim são obrigatórios'}), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Vendas por prato
            cursor.execute('''
                SELECT 
                    ft.nome_prato,
                    ft.categoria,
                    SUM(v.quantidade) as quantidade_total,
                    SUM(v.valor_total) as valor_total
                FROM vendas v
                JOIN fichas_tecnicas ft ON v.ficha_tecnica_id = ft.id
                WHERE DATE(v.data_venda) BETWEEN ? AND ?
                GROUP BY v.ficha_tecnica_id
                ORDER BY valor_total DESC
            ''', (data_inicio, data_fim))
            
            vendas_por_prato = [dict(row) for row in cursor.fetchall()]
            
            # Vendas por dia
            cursor.execute('''
                SELECT 
                    DATE(data_venda) as data,
                    COUNT(*) as total_vendas,
                    SUM(valor_total) as valor_total
                FROM vendas
                WHERE DATE(data_venda) BETWEEN ? AND ?
                GROUP BY DATE(data_venda)
                ORDER BY data
            ''', (data_inicio, data_fim))
            
            vendas_por_dia = [dict(row) for row in cursor.fetchall()]
            
            # Vendas por categoria
            cursor.execute('''
                SELECT 
                    ft.categoria,
                    COUNT(*) as total_vendas,
                    SUM(v.valor_total) as valor_total
                FROM vendas v
                JOIN fichas_tecnicas ft ON v.ficha_tecnica_id = ft.id
                WHERE DATE(v.data_venda) BETWEEN ? AND ?
                GROUP BY ft.categoria
                ORDER BY valor_total DESC
            ''', (data_inicio, data_fim))
            
            vendas_por_categoria = [dict(row) for row in cursor.fetchall()]
            
            # Total geral
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_vendas,
                    SUM(valor_total) as valor_total,
                    AVG(valor_total) as ticket_medio
                FROM vendas
                WHERE DATE(data_venda) BETWEEN ? AND ?
            ''', (data_inicio, data_fim))
            
            totais = dict(cursor.fetchone())
            
            return jsonify({
                'periodo': {
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                },
                'totais': totais,
                'vendas_por_prato': vendas_por_prato,
                'vendas_por_dia': vendas_por_dia,
                'vendas_por_categoria': vendas_por_categoria
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/relatorio/estoque', methods=['GET'])
@token_required
def relatorio_estoque():
    """Gera relatório de estoque atual"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    i.*,
                    (i.estoque_atual * i.custo_unitario / 1000) as valor_estoque,
                    CASE 
                        WHEN i.estoque_atual <= i.estoque_minimo THEN 'critico'
                        WHEN i.estoque_atual <= (i.estoque_minimo * 1.5) THEN 'baixo'
                        ELSE 'normal'
                    END as status_estoque
                FROM ingredientes i
                WHERE i.ativo = 1
                ORDER BY status_estoque DESC, i.nome
            ''')
            
            ingredientes = [dict(row) for row in cursor.fetchall()]
            
            # Calcular totais
            valor_total_estoque = sum(ing['valor_estoque'] for ing in ingredientes)
            criticos = sum(1 for ing in ingredientes if ing['status_estoque'] == 'critico')
            baixos = sum(1 for ing in ingredientes if ing['status_estoque'] == 'baixo')
            
            return jsonify({
                'total_ingredientes': len(ingredientes),
                'valor_total_estoque': valor_total_estoque,
                'criticos': criticos,
                'baixos': baixos,
                'ingredientes': ingredientes
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
