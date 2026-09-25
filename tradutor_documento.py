from .sentencizer import aplicar_patch_sentencizer

aplicar_patch_sentencizer()

import argostranslate.package
import argostranslate.translate


class TradutorDocumento:
    def __init__(self, from_code: str = "en", to_code: str = "pb"):
        self.from_code = from_code
        self.to_code = to_code
        self.translation = self._carregar_traducao()

    def _carregar_traducao(self):
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((l for l in installed_languages if l.code == self.from_code), None)
        to_lang = next((l for l in installed_languages if l.code == self.to_code), None)

        if from_lang is None or to_lang is None or from_lang.get_translation(to_lang) is None:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            pacote = next(
                (p for p in available_packages
                 if p.from_code == self.from_code and p.to_code == self.to_code),
                None
            )
            if pacote is None:
                raise ValueError(f"Pacote {self.from_code} -> {self.to_code} nÃ£o encontrado.")
            argostranslate.package.install_from_path(pacote.download())

            argostranslate.translate.get_installed_languages.cache_clear()
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next(l for l in installed_languages if l.code == self.from_code)
            to_lang = next(l for l in installed_languages if l.code == self.to_code)

        translation = from_lang.get_translation(to_lang)
        if translation is None:
            raise RuntimeError(f"NÃ£o foi possÃ­vel carregar traduÃ§Ã£o {self.from_code} -> {self.to_code}.")
        return translation

    def traduzir_texto(self, texto: str) -> str:
        """Traduz uma Ãºnica string."""
        return self.translation.translate(texto)

    def traduzir_paragrafos(self, paragrafos: list[str]) -> list[str]:
        """Traduz uma lista de parÃ¡grafos, mantendo a ordem e a correspondÃªncia 1:1."""
        return [self.traduzir_texto(paragrafo) for paragrafo in paragrafos]

