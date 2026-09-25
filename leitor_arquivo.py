from io import BytesIO
from docx import Document


def ler_txt(conteudo_bytes: bytes) -> list[str]:
    """LÃª bytes de um .txt e retorna uma lista de parÃ¡grafos (divididos por linha)."""
    texto = conteudo_bytes.decode("utf-8")
    # MantÃ©m cada linha nÃ£o vazia como um "parÃ¡grafo"
    return [linha for linha in texto.splitlines() if linha.strip()]


def ler_docx(conteudo_bytes: bytes) -> list[str]:
    """LÃª bytes de um .docx e retorna a lista de parÃ¡grafos (texto de cada um)."""
    documento = Document(BytesIO(conteudo_bytes))
    return [paragrafo.text for paragrafo in documento.paragraphs if paragrafo.text.strip()]


def extrair_paragrafos(nome_arquivo: str, conteudo_bytes: bytes) -> list[str]:
    """Detecta a extensÃ£o do arquivo e delega para o leitor correto."""
    if nome_arquivo.endswith(".txt"):
        return ler_txt(conteudo_bytes)
    elif nome_arquivo.endswith(".docx"):
        return ler_docx(conteudo_bytes)
    else:
        raise ValueError("Formato de arquivo nÃ£o suportado. Use .txt ou .docx.")

