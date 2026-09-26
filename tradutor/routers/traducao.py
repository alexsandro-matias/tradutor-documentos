from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from tradutor import TradutorDocumento, extrair_paragrafos, gerar_arquivo_saida

router = APIRouter()
tradutor = TradutorDocumento(from_code="en", to_code="pb")

EXTENSOES_PERMITIDAS = (".txt", ".docx")


@router.post("/traduzir")
async def traduzir_arquivo(arquivo: UploadFile = File(...)):
    if not arquivo.filename.endswith(EXTENSOES_PERMITIDAS):
        raise HTTPException(
            status_code=400, detail="Apenas arquivos .txt ou .docx sÃ£o aceitos."
        )

    conteudo_bytes = await arquivo.read()

    try:
        paragrafos_originais = extrair_paragrafos(arquivo.filename, conteudo_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo: {str(e)}")

    if not paragrafos_originais:
        raise HTTPException(
            status_code=400, detail="O arquivo estÃ¡ vazio ou sem texto reconhecÃ­vel."
        )

    try:
        paragrafos_traduzidos = tradutor.traduzir_paragrafos(paragrafos_originais)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao traduzir: {str(e)}")

    conteudo_saida, nome_saida, media_type = gerar_arquivo_saida(
        arquivo.filename, paragrafos_traduzidos
    )

    return StreamingResponse(
        BytesIO(conteudo_saida),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nome_saida}"'},
    )
