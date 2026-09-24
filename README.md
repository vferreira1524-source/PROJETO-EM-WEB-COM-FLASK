ETEBookHub

Sistema web de gerenciamento de biblioteca escolar desenvolvido para
organizar o acervo e facilitar o cadastro, a pesquisa e o controle dos
livros.

📚 Sobre o projeto

O ETEBookHub foi desenvolvido como um sistema de biblioteca escolar
utilizando Python, Flask e SQLite.

A aplicação permite cadastrar e organizar livros, pesquisar o acervo,
visualizar capas, trabalhar com categorias e controlar a disponibilidade
dos livros.

O projeto também possui uma área de usuários com login e cadastro.

✨ Principais funcionalidades

Login de usuários

Cadastro de usuários

Cadastro de livros

Listagem do acervo

Pesquisa por título ou autor

Organização dos livros por ID

Cadastro de autor e categoria

Busca automática de capa

Pré-visualização da capa no cadastro

Busca de informações de categoria

Controle de disponibilidade dos livros

Empréstimo e devolução

Edição de livros

Remoção de livros

Banco de dados SQLite

🛠️ Tecnologias utilizadas

Python

Flask

SQLite

Werkzeug

Requests

HTML

CSS

JavaScript

AdminLTE / Bootstrap

Open Library, utilizada para consulta de capas e informações
relacionadas aos livros

As dependências Python utilizadas pelo projeto estão registradas no
arquivo requirements.txt.

📁 Estrutura principal

A estrutura principal do projeto contém arquivos como:

ETEBookHub/
│
├── app.py
├── database.py
├── google_books.py
├── init_db.py
├── banco.sql
├── requirements.txt
├── README.md
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
└── biblioteca_admin/
    └── ...

A estrutura de pastas pode variar conforme a versão do projeto.

🚀 Como executar o projeto

1. Instalar o Python

Instale o Python no computador.

Durante a instalação do Windows, é recomendado marcar:

Add Python to PATH

Depois confirme a instalação:

python --version

2. Baixar o projeto

Caso o projeto esteja hospedado no GitHub:

git clone URL_DO_REPOSITORIO

Depois entre na pasta do projeto:

cd ETEBookHub

Substitua URL_DO_REPOSITORIO pelo endereço real do seu repositório.

3. Criar um ambiente virtual

No Windows:

python -m venv venv

Ative o ambiente:

venv\Scriptsctivate

Quando estiver ativado, normalmente aparecerá algo semelhante a:

(venv) PS C:\...\ETEBookHub>

4. Instalar as dependências

O projeto possui um arquivo requirements.txt.

Execute:

pip install -r requirements.txt

As dependências atuais incluem Flask, Werkzeug e Requests.

🗄️ Banco de dados

O ETEBookHub utiliza SQLite.

O projeto possui arquivos relacionados à inicialização do banco:

banco.sql
init_db.py
database.py

Antes de executar qualquer script de inicialização, verifique a
estrutura do projeto e o conteúdo do banco atual.

⚠️ Atenção: scripts de inicialização podem criar ou modificar tabelas.
Se já existirem dados importantes, faça uma cópia de segurança antes
de executar qualquer procedimento de inicialização.

▶️ Executando o sistema

Com o ambiente virtual ativado, execute:

python app.py

O Flask deverá mostrar no terminal o endereço local da aplicação.

Normalmente será algo parecido com:

http://127.0.0.1:5000

Abra o endereço informado no navegador.

👤 Usuários

O sistema possui uma área de acesso para usuários.

É possível realizar o cadastro de um novo usuário e posteriormente
utilizar as credenciais para acessar o sistema.

Caso apareça um erro relacionado a uma rota de cadastro, confira se o
nome utilizado no url_for() do HTML corresponde exatamente ao nome da
função registrada no app.py.

📖 Cadastro de livros

Na área de cadastro é possível informar informações como:

Título

Autor

Categoria

Capa

A capa pode ser buscada automaticamente utilizando o título e o autor.

Depois de encontrada, a aplicação apresenta uma prévia da imagem antes
do cadastro.

🖼️ Capas dos livros

O projeto possui o arquivo:

google_books.py

responsável pelas funções relacionadas à busca de informações externas
sobre livros.

Durante o desenvolvimento, a busca de capas foi adaptada para utilizar
capas disponíveis na Open Library.

A consulta depende de uma conexão com a internet.

Se o serviço externo estiver indisponível ou limitar consultas, a capa
poderá não ser encontrada.

🏷️ Categorias

O sistema também possui uma função de consulta de informações
relacionadas à categoria do livro.

As informações encontradas podem ser utilizadas para preencher a
categoria durante o cadastro.

Por exemplo, um livro relacionado a magia e sobrenatural pode ser
classificado como:

Fantasia

🔎 Pesquisa do acervo

O acervo pode ser pesquisado utilizando informações como:

Título
Autor

Os livros são apresentados em ordem crescente de ID.

Exemplo:

1 - Dom Casmurro
2 - Romeu e Julieta
3 - A Cartomante
4 - Harry Potter

A ordenação é feita pelo banco de dados e não altera os IDs existentes.

📚 Status dos livros

O sistema trabalha com a disponibilidade dos livros.

Um livro pode aparecer como:

Disponível

ou

Emprestado

Quando um livro é emprestado, sua disponibilidade é alterada. Após a
devolução, o status pode voltar para disponível.

⚠️ Problemas comuns

ModuleNotFoundError

Exemplo:

ModuleNotFoundError: No module named 'flask'

Solução:

Certifique-se de que o ambiente virtual está ativado e execute:

pip install -r requirements.txt

sqlite3.OperationalError: no such table

Esse erro significa que o SQLite não encontrou a tabela solicitada.

Confira:

se o banco correto está sendo utilizado;

se o banco foi inicializado;

se o arquivo de banco está no local esperado;

se as tabelas existentes correspondem ao código atual.

BuildError

Exemplo:

werkzeug.routing.exceptions.BuildError

Esse erro normalmente ocorre quando o HTML chama uma rota com um nome
diferente daquele registrado no Flask.

Exemplo:

url_for('cadastrarUsuario')

Se a função registrada tiver outro nome, os nomes precisam ser ajustados
para corresponder.

TemplateSyntaxError

Esse erro normalmente está relacionado à estrutura Jinja dos templates.

Confira se todos os blocos estão corretamente fechados:

{% if %}
{% endif %}

e:

{% for %}
{% endfor %}

Erro ao buscar capa ou categoria

As buscas externas dependem de internet e de serviços de terceiros.

Se a consulta não retornar resultados:

verifique a conexão com a internet;

confira a URL consultada;

teste novamente com um título conhecido;

verifique o terminal do Flask para visualizar a resposta da
consulta.

🔐 Segurança antes de publicar no GitHub

Antes de enviar o projeto para um repositório público, não publique
informações privadas.

Evite enviar:

.env
venv/
.venv/
__pycache__/
*.pyc

Também é recomendado verificar se o projeto não contém:

senhas;

tokens;

chaves de API;

informações pessoais;

arquivos temporários.

Banco SQLite

Se o arquivo do banco contiver dados reais de usuários ou outras
informações pessoais, não o publique em um repositório público.

🧹 Arquivos que não precisam ser enviados

O projeto contém arquivos que são gerados automaticamente pelo Python ou
pelo Git.

Exemplos:

__pycache__/
*.pyc
venv/
.venv/

Um arquivo .gitignore pode ser utilizado para evitar que esses
arquivos sejam enviados ao GitHub.

Exemplo:

__pycache__/
*.pyc
venv/
.venv/
.env

Se o banco local contiver dados reais, considere também ignorar o
arquivo SQLite:

*.db

📤 Enviando o projeto para o GitHub

Depois de configurar o repositório remoto, os comandos básicos são:

git add .

Depois:

git commit -m "Atualiza ETEBookHub"

E:

git push

Antes do primeiro push, confira:

git status

para verificar quais arquivos serão enviados.

🎓 Objetivo acadêmico

O ETEBookHub pode ser utilizado como projeto acadêmico para demonstrar
conhecimentos de:

Desenvolvimento Web

Python

Flask

Banco de dados

SQLite

HTML

CSS

JavaScript

CRUD

Integração com serviços externos

Organização de sistemas

👨‍💻 Projeto

ETEBookHub

Sistema de gerenciamento de biblioteca escolar.

Desenvolvido como projeto acadêmico na área de Análise e
Desenvolvimento de Sistemas.

📌 Observação

Este README foi preparado para facilitar a instalação e execução do
projeto por outros usuários.

Caso novas funcionalidades, dependências ou mudanças na estrutura sejam
adicionadas ao ETEBookHub, recomenda-se atualizar este arquivo para
manter as instruções sincronizadas com o projeto.