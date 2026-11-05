import sqlite3

conn = sqlite3.connect("biblioteca.db")

try:
    colunas = {
        coluna[1]
        for coluna in conn.execute("PRAGMA table_info(emprestimo)")
    }

    novas_colunas = {
        "nome_aluno": "TEXT",
        "serie": "TEXT",
        "prazo": "TEXT",
        "observacoes": "TEXT",
        "prazo_alterado_em": "TEXT",
        "prazo_alterado_por": "INTEGER",
    }

    for nome, tipo in novas_colunas.items():
        if nome not in colunas:
            conn.execute(
                f"ALTER TABLE emprestimo ADD COLUMN {nome} {tipo}"
            )
            print(f"Coluna adicionada: {nome}")
        else:
            print(f"Coluna já existe: {nome}")

    conn.commit()
    print("Atualização concluída!")

except sqlite3.Error as erro:
    conn.rollback()
    print("Erro ao atualizar o banco:", erro)

finally:
    conn.close()