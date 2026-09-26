from io import BytesIO
from docx import Document


def gerar_txt(paragrafos_traduzidos: list[str]) -> bytes:
    """Gera bytes de um .txt a partir da lista de parÃ¡grafos traduzidos."""
    texto = "\n".join(paragrafos_traduzidos)
    return texto.encode("utf-8")


def gerar_docx(paragrafos_traduzidos: list[str]) -> bytes:
    """Gera bytes de um novo .docx a partir da lista de parÃ¡grafos traduzidos."""
    documento = Document()
    for paragrafo in paragrafos_traduzidos:
        documento.add_paragraph(paragrafo)

    buffer = BytesIO()
    documento.save(buffer)
    buffer.seek(0)
    return buffer.read()


def gerar_arquivo_saida(nome_arquivo_original: str, paragrafos_traduzidos: list[str]) -> tuple[bytes, str, str]:
    """
    Gera o arquivo de saÃ­da no mesmo formato do original.

    Returns:
        (conteudo_bytes, nome_arquivo_saida, media_type)
    """
    if nome_arquivo_original.endswith(".docx"):
        conteudo = gerar_docx(paragrafos_traduzidos)
        nome_saida = "traduzido_" + nome_arquivo_original
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        conteudo = gerar_txt(paragrafos_traduzidos)
        nome_saida = "traduzido_" + nome_arquivo_original
        media_type = "text/plain"

    return conteudo, nome_saida, media_type

