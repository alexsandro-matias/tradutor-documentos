import os

# Precisa ser a PRIMEIRA coisa a executar no pacote, antes de qualquer import do argostranslate
os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"
os.environ["ARGOS_DEBUG"] = "0"

from .tradutor_documento import TradutorDocumento
from .leitor_arquivo import extrair_paragrafos
from .gerador_arquivo import gerar_arquivo_saida

__all__ = ["TradutorDocumento", "extrair_paragrafos", "gerar_arquivo_saida"]
