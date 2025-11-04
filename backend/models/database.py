import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.environ.get('DATABASE_PATH', '/home/ubuntu/silvess/backend/silvess.db')

def get_db_connection():
    """Cria uma conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager para conexão com banco de dados"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Inicializa o banco de dados com todas as tabelas"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                perfil TEXT DEFAULT 'usuario',
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de ingredientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                unidade_medida TEXT NOT NULL,
                custo_unitario REAL NOT NULL,
                estoque_atual REAL DEFAULT 0,
                estoque_minimo REAL DEFAULT 0,
                fornecedor TEXT,
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de fichas técnicas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fichas_tecnicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_prato TEXT NOT NULL,
                categoria TEXT,
                descricao TEXT,
                porcoes INTEGER DEFAULT 1,
                tempo_preparo INTEGER,
                modo_preparo TEXT,
                validade_horas INTEGER,
                custo_total REAL DEFAULT 0,
                preco_venda REAL DEFAULT 0,
                margem_lucro REAL DEFAULT 0,
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de ingredientes das fichas técnicas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ficha_ingredientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ficha_id INTEGER NOT NULL,
                ingrediente_id INTEGER NOT NULL,
                quantidade_gramas REAL NOT NULL,
                custo_parcial REAL DEFAULT 0,
                FOREIGN KEY (ficha_id) REFERENCES fichas_tecnicas(id) ON DELETE CASCADE,
                FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
            )
        ''')
        
        # Tabela de inventário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inventario DATE NOT NULL,
                ingrediente_id INTEGER NOT NULL,
                quantidade_sistema REAL NOT NULL,
                quantidade_fisica REAL,
                diferenca REAL,
                observacoes TEXT,
                editavel BOOLEAN DEFAULT 1,
                usuario_id INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de movimentações de estoque
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingrediente_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                quantidade REAL NOT NULL,
                data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER,
                observacao TEXT,
                FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabela de cardápios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cardapios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de pratos do cardápio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cardapio_pratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cardapio_id INTEGER NOT NULL,
                ficha_tecnica_id INTEGER NOT NULL,
                disponivel BOOLEAN DEFAULT 1,
                ordem INTEGER DEFAULT 0,
                FOREIGN KEY (cardapio_id) REFERENCES cardapios(id) ON DELETE CASCADE,
                FOREIGN KEY (ficha_tecnica_id) REFERENCES fichas_tecnicas(id)
            )
        ''')
        
        # Tabela de mesas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER UNIQUE NOT NULL,
                qrcode_url TEXT,
                cardapio_id INTEGER,
                ativo BOOLEAN DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cardapio_id) REFERENCES cardapios(id)
            )
        ''')
        
        # Tabela de vendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER,
                ficha_tecnica_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                valor_unitario REAL NOT NULL,
                valor_total REAL NOT NULL,
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id INTEGER,
                FOREIGN KEY (mesa_id) REFERENCES mesas(id),
                FOREIGN KEY (ficha_tecnica_id) REFERENCES fichas_tecnicas(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        conn.commit()
        print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    init_db()
