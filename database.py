import sqlite3

DB = "datafuel.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS venda_produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_produto TEXT,
            descricao TEXT,
            valor_unitario REAL,
            quantidade REAL,
            numero_serie_ecf TEXT,
            valor_total REAL,
            data_importacao TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS venda_diaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            veiculos INTEGER,
            litragem REAL,
            ticket_litragem REAL,
            valor REAL,
            ticket_valor REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS venda_pagamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            forma_pagamento TEXT,
            valor REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS despesa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            categoria TEXT,
            descricao TEXT,
            valor REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS patrimonio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,
            descricao TEXT,
            valor REAL
        )
    """)

    conn.commit()
    conn.close()
