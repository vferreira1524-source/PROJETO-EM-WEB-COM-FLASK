import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash


def conexao():
    conn = sqlite3.connect("biblioteca.db")
    conn.row_factory = sqlite3.Row
    return conn


def buscar_usuario(login):
    conn = conexao()
    usuario = conn.execute(
        "SELECT * FROM usuario WHERE login = ? AND ativo = 1", (login,)
    ).fetchone()
    conn.close()
    return usuario


def cadastrar_usuario(nome, login, senha):
    conn = conexao()
    try:
        cursor = conn.execute(
            "INSERT INTO usuario (nome, login, senha_hash, ativo) VALUES (?, ?, ?, 1)",
            (nome, login, generate_password_hash(senha)),
        )
        conn.commit()
        return cursor.lastrowid, None
    except sqlite3.IntegrityError:
        conn.rollback()
        return None, "login_existente"
    finally:
        conn.close()


def listar_livros(busca=None):

    conn = conexao()

    if busca:
        termo = f"%{busca}%"

        livros = conn.execute(
            """
            SELECT *
            FROM livro
            WHERE titulo LIKE ? OR autor LIKE ?
            ORDER BY id ASC
            """,
            (termo, termo),
        ).fetchall()

    else:
        livros = conn.execute(
            """
            SELECT *
            FROM livro
            ORDER BY id ASC
            """
        ).fetchall()

    conn.close()

    return livros


def buscar_livro(id_livro):
    conn = conexao()
    livro = conn.execute(
        "SELECT * FROM livro WHERE id = ?", (id_livro,)
    ).fetchone()
    conn.close()
    return livro


def contar_status():
    conn = conexao()
    total = conn.execute("SELECT COUNT(*) FROM livro").fetchone()[0]
    disponiveis = conn.execute(
        "SELECT COUNT(*) FROM livro WHERE status = 'disponivel'"
    ).fetchone()[0]
    emprestados = conn.execute(
        "SELECT COUNT(*) FROM livro WHERE status = 'emprestado'"
    ).fetchone()[0]
    conn.close()
    return total, disponiveis, emprestados


def cadastrar_livro(titulo, autor, categoria, img=None):
    conn = conexao()

    conn.execute(
        """INSERT INTO livro
           (titulo, autor, categoria, status, img)
           VALUES (?, ?, ?, 'disponivel', ?)""",
        (titulo, autor, categoria, img)
    )

    conn.commit()
    conn.close()

def editar_livro(id_livro, titulo, autor, categoria):
    conn = conexao()
    conn.execute(
        """UPDATE livro SET titulo = ?, autor = ?, categoria = ?
           WHERE id = ?""",
        (titulo, autor, categoria, id_livro),
    )
    conn.commit()
    conn.close()


def emprestar_livro(id_livro, id_usuario):
    conn = conexao()
    livro = conn.execute(
        "SELECT status FROM livro WHERE id = ?", (id_livro,)
    ).fetchone()
    if livro is None or livro["status"] != "disponivel":
        conn.close()
        return False

    conn.execute(
        "UPDATE livro SET status = 'emprestado' WHERE id = ?", (id_livro,)
    )
    conn.execute(
        """INSERT INTO emprestimo (id_livro, id_usuario, data_emprestimo)
           VALUES (?, ?, ?)""",
        (id_livro, id_usuario, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()
    return True


def devolver_livro(id_livro):
    conn = conexao()
    livro = conn.execute(
        "SELECT status FROM livro WHERE id = ?", (id_livro,)
    ).fetchone()
    if livro is None or livro["status"] != "emprestado":
        conn.close()
        return False

    conn.execute(
        "UPDATE livro SET status = 'disponivel' WHERE id = ?", (id_livro,)
    )
    conn.execute(
        """UPDATE emprestimo SET data_devolucao = ?
           WHERE id_livro = ? AND data_devolucao IS NULL""",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), id_livro),
    )
    conn.commit()
    conn.close()
    return True


def remover_livro(id_livro):
    conn = conexao()
    cursor = conn.execute("DELETE FROM livro WHERE id = ?", (id_livro,))
    conn.commit()
    afetado = cursor.rowcount > 0
    conn.close()
    return afetado

def reiniciar_id_livros():
    conn = conexao()

    conn.execute(
        "DELETE FROM sqlite_sequence WHERE name = ?",
        ("livro",)
    )

    conn.commit()
    conn.close()
