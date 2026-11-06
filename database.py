import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

def formatar_data(data):
    if not data:
        return "-"

    texto = str(data).strip()

    try:
        data_convertida = datetime.fromisoformat(texto)
        return data_convertida.strftime("%d-%m-%Y")

    except ValueError:
        try:
            data_convertida = datetime.strptime(
                texto, "%d-%m-%Y"
            )

            return data_convertida.strftime("%d-%m-%Y")

        except ValueError:
            return texto
    

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



def obter_dados_dashboard():
    conn = conexao()

    try:
        # 1. Empréstimos atrasados e ainda não devolvidos
        atrasados = conn.execute(
            """
            SELECT COUNT(*)
            FROM emprestimo
            WHERE (data_devolucao IS NULL OR TRIM(data_devolucao) = '')
              AND date(prazo) IS NOT NULL
              AND date(prazo) < date('now', 'localtime')
            """
        ).fetchone()[0]

        # 2. Usuários ativos
        usuarios = conn.execute(
            """
            SELECT COUNT(*)
            FROM usuario
            WHERE ativo = 1
            """
        ).fetchone()[0]

        # 3. Preparar os últimos seis meses
        hoje = datetime.now()

        nomes_meses = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]

        meses = []

        for deslocamento in range(5, -1, -1):

            indice = hoje.year * 12 + hoje.month - 1 - deslocamento

            ano, mes_zero = divmod(indice, 12)
            mes = mes_zero + 1

            chave = f"{ano:04d}-{mes:02d}"

            meses.append({
                "chave": chave,
                "mes": f"{nomes_meses[mes_zero]}/{str(ano)[2:]}",
                "quantidade": 0
            })

        # 4. Buscar empréstimos realizados nesses meses
        primeiro_mes = meses[0]["chave"]
        ultimo_mes = meses[-1]["chave"]

        movimentacoes = conn.execute(
            """
            SELECT
                substr(data_emprestimo, 1, 7) AS mes,
                COUNT(*) AS quantidade
            FROM emprestimo
            WHERE substr(data_emprestimo, 1, 7) BETWEEN ? AND ?
            GROUP BY substr(data_emprestimo, 1, 7)
            """,
            (primeiro_mes, ultimo_mes)
        ).fetchall()

        quantidade_por_mes = {
            item["mes"]: item["quantidade"]
            for item in movimentacoes
        }

        emprestimos_mensais = []

        for item in meses:
            emprestimos_mensais.append({
                "mes": item["mes"],
                "quantidade": quantidade_por_mes.get(
                    item["chave"], 0
                )
            })

        # 5. Últimos cinco empréstimos realizados
        recentes = conn.execute(
            """
            SELECT
                e.id,
                e.nome_aluno,
                e.serie,
                e.data_emprestimo,
                e.data_devolucao,
                e.prazo,
                l.titulo AS titulo_livro
            FROM emprestimo e
            INNER JOIN livro l ON l.id = e.id_livro
            ORDER BY e.id DESC
            LIMIT 5
            """
        ).fetchall()

        # 6. Cinco livros mais emprestados
        mais_emprestados = conn.execute(
            """
            SELECT
                l.titulo,
                COUNT(e.id) AS quantidade
            FROM emprestimo e
            INNER JOIN livro l ON l.id = e.id_livro
            GROUP BY l.id, l.titulo
            ORDER BY quantidade DESC, l.titulo ASC
            LIMIT 5
            """
        ).fetchall()

        # 7. Quantidade de livros por categoria
        categorias = conn.execute(
            """
            SELECT
                COALESCE(
                    NULLIF(TRIM(categoria), ''),
                    'Sem categoria'
                ) AS categoria,
                COUNT(*) AS quantidade
            FROM livro
            GROUP BY COALESCE(
                NULLIF(TRIM(categoria), ''),
                'Sem categoria'
            )
            ORDER BY quantidade DESC
            """
        ).fetchall()

        return {
            "atrasados": atrasados,
            "usuarios": usuarios,
            "emprestimos_mensais": emprestimos_mensais,
            "recentes": recentes,
            "mais_emprestados": mais_emprestados,
            "categorias": [dict(item) for item in categorias]
        }

    finally:
        conn.close()


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


def listar_usuarios():
    conn = conexao()

    usuarios = conn.execute(
        """
        SELECT id, nome, login
        FROM usuario
        WHERE ativo = 1
        ORDER BY nome ASC
        """
    ).fetchall()

    conn.close()
    return usuarios


def editar_usuario(id_usuario, nome, login, senha=None):
    conn = conexao()

    try:
        if senha:
            conn.execute(
                """
                UPDATE usuario
                SET nome = ?, login = ?, senha_hash = ?
                WHERE id = ? AND ativo = 1
                """,
                (
                    nome,
                    login,
                    generate_password_hash(senha),
                    id_usuario
                )
            )
        else:
            conn.execute(
                """
                UPDATE usuario
                SET nome = ?, login = ?
                WHERE id = ? AND ativo = 1
                """,
                (nome, login, id_usuario)
            )

        if conn.total_changes == 0:
            conn.rollback()
            return False, "usuario_nao_encontrado"

        conn.commit()
        return True, None

    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "login_existente"

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()