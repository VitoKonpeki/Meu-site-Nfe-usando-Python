# app/models/usuarios.py
import bcrypt
from validate_email import validate_email
from .db import DBconexao  # garante que está importando a função certa

def criar_usuario(email, senha):
    # valida email antes de abrir a conexão
    if not validate_email(email):
        return "email_invalido"
    # elif "@" not in email or "." not in email:
    #     return "email_invalido"

    conn, cursor = DBconexao()

    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return "email_existe"

    depois_do_arroba = email.split("@", 1)[1]
    nome_dominio = depois_do_arroba.split(".", 1)[0]

    if nome_dominio == "admin":
        nivel_usuario = 1
    elif nome_dominio == "operador":
        nivel_usuario = 2
    elif nome_dominio == "visualizador":
        nivel_usuario = 3
    else:
        return "email_sem_acesso"

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("INSERT INTO usuarios (email, senha, nivel) VALUES (?, ?, ?)", (email, senha_hash, nivel_usuario))
    conn.commit()
    conn.close()
    return "ok"


def login_usuario(email, senha):
    conn, cursor = DBconexao()

    cursor.execute("SELECT id, email, senha, nivel FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        return False

    # usuario: (id, email, senha, criado_em)
    senha_db = usuario[2].encode('utf-8')
    if bcrypt.checkpw(senha.encode('utf-8'), senha_db):
        cursor.execute("INSERT INTO log (usuario_id) VALUES (?)", (usuario[0],))
        conn.commit()
        conn.close()
        return {"id": usuario[0], "nivel": usuario[3]}

    conn.close()
    return False
