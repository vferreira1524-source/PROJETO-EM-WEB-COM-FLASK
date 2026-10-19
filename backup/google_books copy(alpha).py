import requests


def buscar_capa(titulo, autor):
    consulta = f"intitle:{titulo}+inauthor:{autor}"

    url = "https://www.googleapis.com/books/v1/volumes"

    parametros = {
        "q": consulta,
        "maxResults": 5,
        "printType": "books"
    }

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=10
        )

        if resposta.status_code != 200:
            return None

        dados = resposta.json()
        livros = dados.get("items", [])

        if not livros:
            return None

        volume_info = livros[0].get("volumeInfo", {})
        imagens = volume_info.get("imageLinks", {})

        return (
            imagens.get("large")
            or imagens.get("medium")
            or imagens.get("thumbnail")
        )

    except requests.RequestException:
        return None