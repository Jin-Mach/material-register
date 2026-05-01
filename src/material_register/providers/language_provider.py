class LanguageProvider:
    DEFAULT_LANGUAGE = "en_GB"
    SUPPORTED_LANGUAGES = ["cs_CZ", "en_GB"]
    current_language = DEFAULT_LANGUAGE

    @classmethod
    def language_init(cls, locale: str) -> None:
        cls.current_language = LanguageProvider._set_language_code(locale)

    @staticmethod
    def _set_language_code(locale: str) -> str:
        if not locale or locale not in LanguageProvider.SUPPORTED_LANGUAGES:
            return LanguageProvider.DEFAULT_LANGUAGE
        return locale