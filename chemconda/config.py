import os
import yaml
from rich.console import Console

CONFIG_FILE = os.path.expanduser('~/.config/chemconda/config.yaml')

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
            cls._instance = super(Config, cls).__new__(cls)
            # load config file and overwrite ENV VARS
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as stream:
                    try:
                        _config_cache = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        raise exc

                # load CHEMCONDA_HOME_PATH from config file
                cls.home_path = cls.home_path if 'CHEMCONDA_HOME_PATH' not in _config_cache else _config_cache['CHEMCONDA_HOME_PATH']

        return cls._instance