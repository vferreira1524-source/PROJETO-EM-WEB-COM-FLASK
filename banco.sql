DROP TABLE IF EXISTS emprestimo;
DROP TABLE IF EXISTS livro;
DROP TABLE IF EXISTS usuario;


CREATE TABLE usuario (
   id integer primary key autoincrement,
   nome varchar(80) not null,
   login varchar(50) not null unique,
   senha_hash varchar(200) not null,
   ativo boolean default 1
);

CREATE TABLE livro(
   id integer primary key autoincrement,
   titulo varchar(150) not null,
   autor varchar(120) not null,
   categoria varchar(60),
   status varchar(20) default 'disponivel',
   imagem blob,
   img varchar(100)
);

CREATE TABLE emprestimo(
   id integer primary key autoincrement,
   id_livro int not null,
   id_usuario int not null,
   data_emprestimo text not null,
   data_devolucao text,
   foreign key ('id_livro') references livro('id'),
   foreign key ('id_usuario') references usuario('id')
);

-- Usuário padrão: login "admin" / senha "admin123" (hash gerado pelo init_db.py)
insert into livro(titulo, autor, categoria, status)
values('Dom Casmurro', 'Machado de Assis', 'Romance', 'disponivel'),
      ('O Cortiço', 'Aluísio Azevedo', 'Romance', 'disponivel'),
      ('Vidas Secas', 'Graciliano Ramos', 'Romance', 'emprestado');
