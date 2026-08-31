from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler


class TextFileHandler:
    @staticmethod
    def load_document(document_name: str) -> tuple[bool, str]:
        document_path = PathsProvider.documents / document_name
        try:
            if not document_path.exists():
                document_path.touch()
            return True, document_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return True, ""
        except OSError as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False, ""

    @staticmethod
    def save_document(document_name: str, document_text: str) -> bool:
        document_path = PathsProvider.documents / document_name
        if not document_path.exists():
            ErrorHandler.handle_error(
                f"Document path not exists: {TextFileHandler.__name__}", "app", "error"
            )
            return False
        try:
            document_path.write_text(document_text, encoding="utf-8")
            return True
        except OSError as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False
