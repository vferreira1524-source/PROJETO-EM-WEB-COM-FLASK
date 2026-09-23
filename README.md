# Biblioteca Escolar (estilo AdminLTE)

Este projeto é uma reformulação do sistema **Biblioteca Escolar com login**,
seguindo como base a estrutura do projeto **catalogo-prod** (Flask + SQLite +
tema AdminLTE 4 / Bootstrap 5).

## O que foi seguido do projeto-base (catalogo-prod)
- Layout AdminLTE completo (`templates/admin/base.html`), com sidebar, header e footer.
- Mesma convenção de rotas/funções: `listarLivros`, `cadastrarLivro`, `editarLivro`
  (equivalentes a `listarCategoria`, `cadastrarCategoria`, `editarCategoria`).
- Mesmo padrão de acesso ao banco via `conexao()` em `database.py` e uso de
  `banco.sql` + `init_db.py` para criar/popular o banco.
- Mesma organização de pastas: `templates/admin/`, `static/css/dist/` (assets do AdminLTE).

## O que foi adaptado para o domínio da Biblioteca
- Domínio trocado de "categoria/produto" para **livro** (com empréstimo/devolução).
- Login mantido (sessão do Flask + senha com hash), já que o próprio schema do
  catalogo-prod reservava uma tabela `usuario` para isso.
- Tabela extra `emprestimo` para manter histórico de empréstimos/devoluções.
- Painel inicial (`/`) com indicadores (total de livros, disponíveis, emprestados).

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python init_db.py      # cria biblioteca.db e o usuário admin padrão
python app.py          # roda em http://localhost:5005
```

**Login padrão:** usuário `admin` / senha `admin123` (troque depois de testar).

## Estrutura
```
biblioteca_admin/
├── app.py
├── database.py
├── banco.sql
├── init_db.py
├── requirements.txt
├── static/css/dist/        # AdminLTE (css, js, assets)
└── templates/admin/
    ├── base.html
    ├── login.html
    ├── index.html
    ├── listar_livros.html
    ├── cadastrar_livro.html
    └── editar_livro.html
```


### Correção de rota
A tela de cadastro público usa o endpoint `cadastro_usuario`, evitando BuildError causado por referência ao nome interno da função.
