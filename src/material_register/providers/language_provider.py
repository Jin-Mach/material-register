from material_register.config.language_constants import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
)


class LanguageProvider:
    CURRENT_LANGUAGE = DEFAULT_LANGUAGE

    @classmethod
    def language_init(cls, locale: str) -> None:
        cls.CURRENT_LANGUAGE = LanguageProvider._set_language_code(locale)

    @staticmethod
    def _set_language_code(locale: str) -> str:
        if not locale or locale not in SUPPORTED_LANGUAGES:
            return DEFAULT_LANGUAGE
        return locale
