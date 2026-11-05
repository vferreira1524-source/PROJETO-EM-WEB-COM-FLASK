
import os
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from google_books import buscar_dados_livro

from database import (
    buscar_livro,
    buscar_usuario,
    buscar_usuario_por_id,
    cadastrar_livro,
    cadastrar_usuario,
    contar_status,
    devolver_livro,
    editar_livro,
    editar_emprestimo,
    emprestar_livro,
    listar_emprestimos,
    listar_livros,
    remover_livro,
)

app = Flask(__name__)
import os

print("PASTA RAIZ:", app.root_path)
print("PASTA TEMPLATES:", app.template_folder)
print(
    "ARQUIVO ENCONTRADO:",
    os.path.isfile(
        os.path.join(
            app.root_path,
            "templates",
            "admin",
            "listar_emprestimos.html"
        )
    )
)

from pathlib import Path

print("\n--- PROCURANDO TEMPLATE ---")

for arquivo in Path(app.root_path).rglob("*emprestimos*"):
    print("ENCONTRADO:", arquivo)
    
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "chave-secreta-biblioteca-troque-em-producao"
)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("usuario_id") is None:
            flash("Entre com sua conta para acessar o acervo.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_id") is not None:
        return redirect(url_for("index"))

    if request.method == "POST":
        usuario_login = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        usuario = buscar_usuario(usuario_login)

        if usuario is None or not check_password_hash(
            usuario["senha_hash"], senha
        ):
            flash("Usuário ou senha inválidos.", "danger")
            return render_template(
                "admin/login.html",
                usuario=usuario_login
            )

        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]

        flash("Login realizado com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("admin/login.html", usuario="")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    total, disponiveis, emprestados = contar_status()

    return render_template(
        "admin/index.html",
        total=total,
        disponiveis=disponiveis,
        emprestados=emprestados,
    )


@app.route(
    "/cadastro_usuario",
    methods=["GET", "POST"],
    endpoint="cadastro_usuario"
)
def cadastroUsuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        login_usuario = request.form.get("login", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not nome or not login_usuario or not senha:
            flash("Preencha nome, usuário e senha.", "danger")
            return render_template("admin/cadastro_usuario_login.html")

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template("admin/cadastro_usuario_login.html")

        if senha != confirmar_senha:
            flash("As senhas não conferem.", "danger")
            return render_template("admin/cadastro_usuario_login.html")

        _, erro = cadastrar_usuario(nome, login_usuario, senha)

        if erro == "login_existente":
            flash(
                "Esse nome de usuário já está cadastrado. Escolha outro.",
                "warning"
            )
            return render_template("admin/cadastro_usuario_login.html")

        flash(f'Usuário "{nome}" cadastrado com sucesso.', "success")
        return redirect(url_for("login"))

    return render_template("admin/cadastro_usuario_login.html")


@app.route("/cadastrar_usuario", methods=["GET", "POST"])
@login_required
def cadastrarUsuarioAdmin():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        login_usuario = request.form.get("login", "").strip()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not nome or not login_usuario or not senha:
            flash("Preencha nome, usuário e senha.", "danger")
            return render_template("admin/cadastrar_usuario.html")

        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template("admin/cadastrar_usuario.html")

        if senha != confirmar_senha:
            flash("As senhas não conferem.", "danger")
            return render_template("admin/cadastrar_usuario.html")

        _, erro = cadastrar_usuario(nome, login_usuario, senha)

        if erro == "login_existente":
            flash(
                "Esse nome de usuário já está cadastrado. Escolha outro.",
                "warning"
            )
            return render_template("admin/cadastrar_usuario.html")

        flash(f'Usuário "{nome}" cadastrado com sucesso.', "success")
        return redirect(url_for("index"))

    return render_template("admin/cadastrar_usuario.html")


@app.route("/listar_livros")
@login_required
def listarLivros():
    busca = request.args.get("busca", "").strip()
    livros = listar_livros(busca if busca else None)

    return render_template(
        "admin/listar_livros.html",
        livros=livros,
        busca=busca
    )

@app.route("/emprestimos")
@login_required
def listarEmprestimos():
    emprestimos = listar_emprestimos()

    return render_template(
        "admin/listar_emprestimos.html",
        emprestimos=emprestimos
    )

@app.route(
    "/editar_emprestimo/<int:id_emprestimo>",
    methods=["POST"]
)
@login_required
def editarEmprestimo(id_emprestimo):

    nome_aluno = request.form.get("nome_aluno", "").strip()
    serie = request.form.get("serie", "").strip()
    prazo = request.form.get("prazo", "").strip()
    observacoes = request.form.get("observacoes", "").strip()
    senha_admin = request.form.get("senha_admin", "")

    if not nome_aluno or not serie or not prazo:
        flash("Preencha nome do aluno, série e prazo.", "danger")
        return redirect(url_for("listarEmprestimos"))

    # Localiza o empréstimo atual
    emprestimos = listar_emprestimos()

    emprestimo = next(
        (
            item for item in emprestimos
            if item["id_emprestimo"] == id_emprestimo
        ),
        None
    )

    if emprestimo is None or emprestimo["data_devolucao"] is not None:
        flash("Empréstimo não encontrado ou já devolvido.", "danger")
        return redirect(url_for("listarEmprestimos"))

    # Verifica se o prazo foi alterado
    prazo_alterado = emprestimo["prazo"] != prazo

    if prazo_alterado:
        usuario = buscar_usuario_por_id(session["usuario_id"])

        if (
            usuario is None
            or not senha_admin
            or not check_password_hash(usuario["senha_hash"], senha_admin)
        ):
            flash("Senha do administrador incorreta.", "danger")
            return redirect(url_for("listarEmprestimos"))

    # Validação da data
    try:
        data_prazo = datetime.strptime(prazo, "%Y-%m-%d").date()

        if data_prazo < datetime.today().date():
            flash("O prazo não pode ser uma data passada.", "danger")
            return redirect(url_for("listarEmprestimos"))

    except ValueError:
        flash("Informe uma data válida.", "danger")
        return redirect(url_for("listarEmprestimos"))

    # Salva as alterações
    resultado = editar_emprestimo(
        id_emprestimo,
        nome_aluno,
        serie,
        prazo,
        observacoes,
        session["usuario_id"]
    )

    if resultado:
        flash("Empréstimo atualizado com sucesso!", "success")
    else:
        flash("Não foi possível atualizar o empréstimo.", "danger")

    return redirect(url_for("listarEmprestimos"))


@app.route("/cadastrar_livro", methods=["GET", "POST"])
@login_required
def cadastrarLivro():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        categoria = request.form.get("categoria", "").strip()
        img = request.form.get("img", "").strip()

        if titulo and autor:
            cadastrar_livro(titulo, autor, categoria, img)
            flash(f'"{titulo}" foi cadastrado no acervo.', "success")
            return redirect(url_for("listarLivros"))

        flash("Preencha ao menos título e autor.", "danger")

    return render_template("admin/cadastrar_livro.html")


@app.route("/editar_livro/<int:id_livro>", methods=["GET", "POST"])
@login_required
def editarLivro(id_livro):
    livro = buscar_livro(id_livro)

    if livro is None:
        flash("Livro não encontrado.", "danger")
        return redirect(url_for("listarLivros"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        categoria = request.form.get("categoria", "").strip()

        if titulo and autor:
            editar_livro(id_livro, titulo, autor, categoria)
            flash("Livro atualizado com sucesso.", "success")
            return redirect(url_for("listarLivros"))

        flash("Preencha ao menos título e autor.", "danger")

    return render_template("admin/editar_livro.html", livro=livro)


@app.route("/emprestar/<int:id_livro>", methods=["POST"])
@login_required
def emprestarLivro(id_livro):
    nome_aluno = request.form.get("nome_aluno", "").strip()
    serie = request.form.get("serie", "").strip()
    prazo = request.form.get("prazo", "").strip()
    observacoes = request.form.get("observacoes", "").strip()

    if not nome_aluno or not serie or not prazo:
        flash("Preencha nome do aluno, série e prazo.", "danger")
        return redirect(url_for("listarLivros"))

    try:
        data_prazo = datetime.strptime(prazo, "%Y-%m-%d").date()

        if data_prazo < datetime.today().date():
            flash("O prazo não pode ser uma data passada.", "danger")
            return redirect(url_for("listarLivros"))

    except ValueError:
        flash("Informe uma data de prazo válida.", "danger")
        return redirect(url_for("listarLivros"))

    if emprestar_livro(
        id_livro,
        session["usuario_id"],
        nome_aluno,
        serie,
        prazo,
        observacoes
    ):
        flash(
            f"Livro emprestado para {nome_aluno} com sucesso!",
            "success"
        )
    else:
        flash(
            "Não foi possível emprestar: o livro está indisponível.",
            "danger"
        )

    return redirect(url_for("listarLivros"))


@app.route("/devolver/<int:id_livro>", methods=["POST"])
@login_required
def devolverLivro(id_livro):
    if devolver_livro(id_livro):
        flash("Devolução registrada. Obrigado!", "success")
    else:
        flash(
            "Não foi possível devolver: o livro já está disponível.",
            "danger"
        )

    return redirect(url_for("listarLivros"))


@app.route("/remover_livro/<int:id_livro>", methods=["POST"])
@login_required
def removerLivro(id_livro):
    if remover_livro(id_livro):
        flash("Livro removido do acervo.", "success")
    else:
        flash("Livro não encontrado.", "danger")

    return redirect(url_for("listarLivros"))


@app.route("/buscar_dados_livro")
@login_required
def buscarDadosLivro():
    titulo = request.args.get("titulo", "").strip()
    autor = request.args.get("autor", "").strip()

    if not titulo:
        return {
            "capa": None,
            "categoria": None,
            "erro": "Informe o título do livro."
        }

    return buscar_dados_livro(titulo, autor)


if __name__ == "__main__":
    app.run(debug=True, port=5005)
