from material_register.providers.download_provider import DownloadProvider
from material_register.providers.file_provider import FileProvider
from material_register.ui.setup.error_texts import ErrorTexts
from src.material_register.providers.language_provider import LanguageProvider
from src.material_register.providers.paths_provider import PathsProvider
from src.material_register.providers.texts_provider import TextsProvider
from src.material_register.ui.setup.ui_texts import UiTexts


class SetupInit:

    @classmethod
    def setup_init(cls) -> tuple[bool, str]:
        try:
            invalid_files = FileProvider.check_missing_files(PathsProvider.resources)
            if invalid_files:
                if DownloadProvider.is_ready_for_download(PathsProvider.resources):
                    if not DownloadProvider.download_files(invalid_files, PathsProvider.resources):
                        return False, "DOWNLOAD_FAILED"
                else:
                    return False, "RESOURCES_MISSING"
            TextsProvider.provider_init(LanguageProvider.current_language, PathsProvider.resources)
            if not TextsProvider.UI_TEXTS or not TextsProvider.ERROR_TEXTS:
                return False, "TEXTS_LOAD_FAILED"
            UiTexts.setup_init(TextsProvider.UI_TEXTS)
            ErrorTexts.setup_init(TextsProvider.ERROR_TEXTS)
            return True, ""
        except Exception as e:
            print(e)
            return False, "UNKNOWN_ERROR"