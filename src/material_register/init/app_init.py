from pathlib import Path

from PySide6.QtCore import QLocale

from src.material_register.providers.texts_provider import TextsProvider
from src.material_register.providers.language_provider import LanguageProvider
from src.material_register.providers.root_provider import RootProvider


class AppInit:

    @staticmethod
    def init_app() -> bool:
        try:
            RootProvider.paths_init()
            if RootProvider.root is None:
                return False
            LanguageProvider.language_init(QLocale().name())
            AppInit._basic_setup(LanguageProvider.current_language, RootProvider.resources)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def _basic_setup(current_language: str, resources_path: Path) -> None:
        TextsProvider.provider_init(current_language, resources_path)