import requests


def buscar_capa(titulo, autor=""):
    consulta = f"{titulo} {autor}".strip()

    url = "https://openlibrary.org/search.json"

    parametros = {
        "q": consulta,
        "limit": 10
    }

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=10,
            headers={
                "User-Agent": "ETEBookHub/1.0"
            }
        )

        print("STATUS:", resposta.status_code)
        print("URL:", resposta.url)

        if resposta.status_code != 200:
            print("ERRO:", resposta.text)
            return None

        dados = resposta.json()

        livros = dados.get("docs", [])

        print("RESULTADOS:", len(livros))

        for livro in livros:
            capa_id = livro.get("cover_i")

            if capa_id:
                return f"https://covers.openlibrary.org/b/id/{capa_id}-L.jpg"

        return None

    except requests.RequestException as erro:
        print("ERRO DE CONEXÃO:", erro)
        return None

def buscar_categoria(titulo, autor=""):
    consulta = f"{titulo} {autor}".strip()

    url = "https://openlibrary.org/search.json"

    parametros = {
        "q": consulta,
        "limit": 10,
        "fields": "title,author_name,subject,subject_facet"
    }

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=10,
            headers={
                "User-Agent": "ETEBookHub/1.0"
            }
        )

        if resposta.status_code != 200:
            return None

        dados = resposta.json()
        livros = dados.get("docs", [])

        assuntos = []

        for livro in livros:
            assuntos.extend(livro.get("subject", []))
            assuntos.extend(livro.get("subject_facet", []))

        # Junta tudo em letras minúsculas para facilitar a busca
        assuntos_texto = " ".join(assuntos).lower()

        # Categorias do ETEBookHub
        if any(palavra in assuntos_texto for palavra in [
            "fantasy",
            "magic",
            "witch",
            "wizard",
            "vampire",
            "monster"
        ]):
            return "Fantasia"

        if any(palavra in assuntos_texto for palavra in [
            "science fiction",
            "science-fiction",
            "space",
            "robot",
            "future"
        ]):
            return "Ficção Científica"

        if any(palavra in assuntos_texto for palavra in [
            "romance",
            "love stories",
            "love"
        ]):
            return "Romance"

        if any(palavra in assuntos_texto for palavra in [
            "mystery",
            "detective",
            "crime",
            "murder"
        ]):
            return "Mistério"

        if any(palavra in assuntos_texto for palavra in [
            "horror",
            "horrors",
            "ghost"
        ]):
            return "Terror"

        if any(palavra in assuntos_texto for palavra in [
            "history",
            "historical"
        ]):
            return "História"

        if any(palavra in assuntos_texto for palavra in [
            "biography",
            "autobiography"
        ]):
            return "Biografia"

        if any(palavra in assuntos_texto for palavra in [
            "children",
            "juvenile",
            "school stories"
        ]):
            return "Infantil / Juvenil"

        if any(palavra in assuntos_texto for palavra in [
            "adventure",
            "adventures"
        ]):
            return "Aventura"

        if any(palavra in assuntos_texto for palavra in [
            "poetry",
            "poems"
        ]):
            return "Poesia"

        if any(palavra in assuntos_texto for palavra in [
            "religion",
            "christian",
            "bible"
        ]):
            return "Religião"

        return "Literatura"

    except requests.RequestException as erro:
        print("ERRO DE CONEXÃO:", erro)
        return None