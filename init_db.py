import sqlite3

from werkzeug.security import generate_password_hash


def init_db():
    conn = sqlite3.connect("biblioteca.db")
    with open("banco.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # Usuário padrão para o primeiro acesso (login: admin / senha: admin123)
    conn.execute(
        "INSERT INTO usuario (nome, login, senha_hash, ativo) VALUES (?, ?, ?, 1)",
        ("Administrador", "admin", generate_password_hash("admin123")),
    )

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")
    print('Login padrão -> usuário: "admin" | senha: "admin123"')


if __name__ == "__main__":
    init_db()
