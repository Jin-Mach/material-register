from src.material_register.providers.language_provider import LanguageProvider
from src.material_register.providers.root_provider import RootProvider
from src.material_register.providers.texts_provider import TextsProvider
from src.material_register.ui.setup.texts_setup import TextsSetup


class SetupInit:

    @classmethod
    def setup_init(cls) -> bool:
        try:
            TextsProvider.provider_init(LanguageProvider.current_language, RootProvider.resources)
            if not TextsProvider.UI_TEXTS:
                return False
            TextsSetup.setup_init(TextsProvider.UI_TEXTS)
            return True
        except Exception as e:
            print(e)
            return False