from PySide6.QtCore import QLocale

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
            return True
        except Exception as e:
            print(e)
            return False