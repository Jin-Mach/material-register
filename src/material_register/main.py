from src.material_register.providers.root_provider import RootProvider

if __name__ == "__main__":
    RootProvider.paths_init()
    print("root", RootProvider.root)