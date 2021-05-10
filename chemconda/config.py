from rich.console import Console

class Config(object):
    _instance = None
    console = Console()
    # Args defined here
    home_path = os.getenv("CHEMCONDA_HOME_PATH", None)
    # CHEMCONDA_REMOTE_REPO
    remote_repo = os.getenv("CHEMCONDA_REMOTE_REPO", "https://repo.anaconda.com/miniconda")
    # CHEMCONDA_INSTALLER
    installer = os.getenv("CHEMCONDA_INSTALLER", "Miniconda3-py39_4.9.2-Linux-x86_64.sh")
    # CHEMCONDA_LOCAL_TMP
    download_dir = os.getenv("CHEMCONDA_DOWNLOAD_DIR", "/tmp")
    # CHEMCONDA_INSTALLER_PATH
    installer_path = os.getenv("CHEMCONDA_INSTALLER_PATH", os.path.join(download_dir, installer))

    def __new__(cls):
        if cls._instance is None:
            cls.console.print('Creating the object')
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance