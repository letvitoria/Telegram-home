import sqlite3
from sqlite3 import Error
from flask import request
from datetime import datetime
from flask import session


def conectar_db():
    conectar = sqlite3.connect("cadastros.db")
    return conectar


def criar_tabela_usuarios():
    conn= conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
              CREATE TABLE IF NOT EXISTS usuarios(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nome TEXT NOT NULL,
              username TEXT NOT NULL UNIQUE,
              matricula TEXT NOT NULL UNIQUE,
              cpf TEXT NOT NULL UNIQUE,
              telefone TEXT NOT NULL UNIQUE,
              setor TEXT NOT NULL)
              ''')
#criando tabela acessos (guardar os dados de acesso)
def criar_tabela_acessos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
              CREATE TABLE IF NOT EXISTS acessos(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              usuario TEXT NOT NULL,
              data_hora TEXT NOT NULL)
              ''')
    conn.commit()
    conn.close()


def adicionar_usuario(nome, username, matricula, cpf, telefone, setor):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        # Verifica username (note a vírgula após username para criar uma tupla)
        cursor.execute("SELECT username FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError("Nome de usuário já está em uso")
        
        # Verifica CPF
        cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
        if cursor.fetchone():
            raise ValueError("CPF já cadastrado")
        
        # Verifica matrícula
        cursor.execute("SELECT matricula FROM usuarios WHERE matricula = ?", (matricula,))
        if cursor.fetchone():
            raise ValueError("Matrícula já cadastrada")
        
        # Verifica telefone
        cursor.execute("SELECT telefone FROM usuarios WHERE telefone = ?", (telefone,))
        if cursor.fetchone():
            raise ValueError("Telefone já cadastrado")

        cursor.execute("""
        INSERT INTO usuarios (nome, username, matricula, cpf, telefone, setor) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, username, matricula, cpf, telefone, setor))
        conn.commit()
        return True
        
    except ValueError as e:
        conn.rollback()
        raise  # Re-lança a exceção para ser tratada na rota
    except Exception as e:
        conn.rollback()
        raise Exception("Erro desconhecido ao cadastrar usuário")
    finally:
        conn.close()

def inserir_dados(nome, username, matricula, cpf, telefone, setor):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO usuarios (nome, username, matricula, cpf, telefone, setor) VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, username, matricula, cpf, telefone, setor))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro ao inserir dados: {e}")
    finally:
        conn.close()


def registrar_acesso(usuario):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO acessos (usuario, data_hora) VALUES (?, ?)
    ''', (usuario, data_hora))
    conn.commit()
    conn.close()

def middleware_registrar_acesso(func):
    def wrapper(*args, **kwargs):
        # Obtém o usuário da sessão
        usuario = session.get('usuario_logado',None)
        if usuario:
            registrar_acesso(usuario)
        return func(*args, **kwargs)
    return wrapper

