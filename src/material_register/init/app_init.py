from src.material_register.providers.root_provider import RootProvider


class AppInit:

    @staticmethod
    def init_app() -> bool:
        try:
            RootProvider.paths_init()
            if RootProvider.root is None:
                return False
            return True
        except Exception as e:
            print(e)
            return False