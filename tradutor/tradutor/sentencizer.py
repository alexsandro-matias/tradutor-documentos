import re
import argostranslate.sbd as sbd


class RegexSentencizer(sbd.ISentenceBoundaryDetectionModel):
    """Divide o texto em frases via regex, sem depender de download de modelo (Stanza/SpaCy)."""

    def __init__(self, pkg):
        self.pkg = pkg

    def split_sentences(self, text):
        frases = re.split(r'(?<=[.!?])\s+', text.strip())
        return [f for f in frases if f]


def aplicar_patch_sentencizer():
    """Substitui o MiniSBDSentencizer padrÃ£o pelo RegexSentencizer local (evita downloads)."""
    import argostranslate.translate as at_translate
    at_translate.MiniSBDSentencizer = RegexSentencizer
    sbd.MiniSBDSentencizer = RegexSentencizer

