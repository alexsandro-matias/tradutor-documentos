import os


def configurar_ambiente():
    """Configura variáveis de ambiente do Argos Translate antes de qualquer import."""
    os.environ["ARGOS_CHUNK_TYPE"] = "MINISBD"
    os.environ["ARGOS_DEBUG"] = "0"
