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



def emprestar_livro(
    id_livro,
    id_usuario,
    nome_aluno,
    serie,
    prazo,
    observacoes=""
):
    conn = conexao()

    try:
        # Verifica se o livro está disponível
        livro = conn.execute(
            "SELECT status FROM livro WHERE id = ?",
            (id_livro,)
        ).fetchone()

        if livro is None or livro["status"] != "disponivel":
            return False

        # Atualiza o status do livro
        cursor = conn.execute(
            """UPDATE livro
               SET status = 'emprestado'
               WHERE id = ? AND status = 'disponivel'""",
            (id_livro,)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            return False

        # Registra os dados do empréstimo
        conn.execute(
            """
            INSERT INTO emprestimo (
                id_livro,
                id_usuario,
                data_emprestimo,
                nome_aluno,
                serie,
                prazo,
                observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_livro,
                id_usuario,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                nome_aluno,
                serie,
                prazo,
                observacoes
            )
        )

        conn.commit()
        return True

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


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
def buscar_usuario_por_id(id_usuario):
    conn = conexao()

    usuario = conn.execute(
        """
        SELECT *
        FROM usuario
        WHERE id = ? AND ativo = 1
        """,
        (id_usuario,)
    ).fetchone()

    conn.close()
    return usuario


def listar_emprestimos():
    conn = conexao()

    emprestimos = conn.execute(
        """
        SELECT
            e.id AS id_emprestimo,
            e.id_livro,
            e.id_usuario,
            e.nome_aluno,
            e.serie,
            e.data_emprestimo,
            e.data_devolucao,
            e.prazo,
            e.observacoes,
            e.prazo_alterado_em,
            l.titulo AS titulo_livro,
            l.autor AS autor_livro
        FROM emprestimo e
        INNER JOIN livro l ON l.id = e.id_livro
        ORDER BY e.id DESC
        """
    ).fetchall()

    conn.close()
    return emprestimos


def editar_emprestimo(
    id_emprestimo,
    nome_aluno,
    serie,
    prazo,
    observacoes,
    id_usuario
):
    conn = conexao()

    try:
        emprestimo = conn.execute(
            """
            SELECT prazo
            FROM emprestimo
            WHERE id = ? AND data_devolucao IS NULL
            """,
            (id_emprestimo,)
        ).fetchone()

        if emprestimo is None:
            return False

        # Verifica se o prazo realmente foi alterado
        prazo_alterado = emprestimo["prazo"] != prazo

        if prazo_alterado:
            conn.execute(
                """
                UPDATE emprestimo
                SET
                    nome_aluno = ?,
                    serie = ?,
                    prazo = ?,
                    observacoes = ?,
                    prazo_alterado_em = ?,
                    prazo_alterado_por = ?
                WHERE id = ? AND data_devolucao IS NULL
                """,
                (
                    nome_aluno,
                    serie,
                    prazo,
                    observacoes,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    id_usuario,
                    id_emprestimo
                )
            )
        else:
            conn.execute(
                """
                UPDATE emprestimo
                SET
                    nome_aluno = ?,
                    serie = ?,
                    observacoes = ?
                WHERE id = ? AND data_devolucao IS NULL
                """,
                (
                    nome_aluno,
                    serie,
                    observacoes,
                    id_emprestimo
                )
            )

        conn.commit()
        return True

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()