import requests


def buscar_dados_livro(titulo, autor=""):

    resultado = {
        "capa": None,
        "categoria": None
    }

    titulo = titulo.strip()
    autor = autor.strip()

    if not titulo:
        return resultado

    try:

        # --------------------------------
        # BUSCAR LIVRO NA OPEN LIBRARY
        # --------------------------------

        url = "https://openlibrary.org/search.json"

        params = {
            "title": titulo,
            "author": autor,
            "limit": 10
        }

        resposta = requests.get(
            url,
            params=params,
            timeout=10
        )

        print("STATUS OPEN LIBRARY:", resposta.status_code)

        if resposta.status_code != 200:
            return resultado

        dados = resposta.json()

        livros = dados.get("docs", [])

        print("LIVROS ENCONTRADOS:", len(livros))

        if not livros:
            return resultado

        print("PRIMEIRO LIVRO:")
        print(livros[0])

        # --------------------------------
        # PROCURAR CAPA
        # --------------------------------

        for livro in livros:

            capa_id = livro.get("cover_i")

            if capa_id:

                resultado["capa"] = (
                    f"https://covers.openlibrary.org/b/id/"
                    f"{capa_id}-L.jpg"
                )

                break

        # --------------------------------
        # PROCURAR CATEGORIA
        # --------------------------------

        todos_assuntos = []

        # Tenta encontrar assuntos diretamente
        # nos resultados da pesquisa

        for livro in livros:

            assuntos = livro.get("subject", [])

            if assuntos:
                todos_assuntos.extend(assuntos)

            subject_facet = livro.get(
                "subject_facet",
                []
            )

            if subject_facet:
                todos_assuntos.extend(
                    subject_facet
                )

        # --------------------------------
        # SE NÃO ENCONTROU ASSUNTOS,
        # CONSULTA A OBRA DIRETAMENTE
        # --------------------------------

        if not todos_assuntos:

            chave_obra = livros[0].get("key")

            print(
                "CHAVE DA OBRA:",
                chave_obra
            )

            if chave_obra:

                try:

                    url_obra = (
                        f"https://openlibrary.org"
                        f"{chave_obra}.json"
                    )

                    resposta_obra = requests.get(
                        url_obra,
                        timeout=10
                    )

                    print(
                        "STATUS OBRA:",
                        resposta_obra.status_code
                    )

                    if resposta_obra.status_code == 200:

                        dados_obra = (
                            resposta_obra.json()
                        )

                        assuntos_obra = (
                            dados_obra.get(
                                "subjects",
                                []
                            )
                        )

                        print(
                            "ASSUNTOS DA OBRA:",
                            assuntos_obra[:30]
                        )

                        if assuntos_obra:

                            todos_assuntos.extend(
                                assuntos_obra
                            )

                except Exception as erro:

                    print(
                        "ERRO AO BUSCAR "
                        "ASSUNTOS DA OBRA:",
                        erro
                    )

        # --------------------------------
        # IDENTIFICAR CATEGORIA
        # --------------------------------

        print(
            "TOTAL DE ASSUNTOS:",
            len(todos_assuntos)
        )

        print(
            "ASSUNTOS ENCONTRADOS:",
            todos_assuntos[:30]
        )

        resultado["categoria"] = (
            identificar_categoria(
                todos_assuntos
            )
        )

    except Exception as erro:

        print(
            "ERRO AO BUSCAR DADOS:",
            erro
        )

    return resultado


def identificar_categoria(assuntos):

    if not assuntos:
        return None

    assuntos_texto = " ".join(
        str(assunto).lower()
        for assunto in assuntos
    )

    categorias = {

        "Fantasia": [
    "fantasy",
    "fantasies",
    "fantasy fiction",
    "magic",
    "magical",
    "magic in fiction",
    "magic and supernatural",
    "supernatural",
    "witches",
    "witch",
    "witches in fiction",
    "wizards",
    "wizard",
    "wizards in fiction",
    "vampires",
    "vampire",
    "vampires in fiction",
    "monsters",
    "monster",
    "monsters in fiction",
    "alchemy",
    "harry potter"
],
        

        "Aventura": [
            "adventure",
            "adventures"
        ],

        "Romance": [
            "romance",
            "love stories"
        ],

        "Mistério": [
            "mystery",
            "detective",
            "detective stories"
        ],

        "Terror": [
            "horror",
            "ghosts",
            "terror"
        ],

        "Ficção Científica": [
            "science fiction",
            "science-fiction",
            "sci-fi"
        ],

        "História": [
            "history",
            "historical"
        ],

        "Biografia": [
            "biography",
            "autobiography"
        ],

        "Infantil": [
            "children",
            "children's books"
        ],

        "Juvenil": [
            "young adult",
            "teen",
            "juvenile",
            "school stories",
            "school life"
        ]
    }

    for categoria, palavras in categorias.items():

        for palavra in palavras:

            if palavra in assuntos_texto:

                return categoria

    return "Outros"