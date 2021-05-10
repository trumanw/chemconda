import os
import yaml
from rich.console import Console

CONFIG_FILE = os.path.expanduser('~/.config/chemconda/config.yaml')

class Config(object):
    _instance = None
    console = Console()
    # Args defined here
    _home_path = os.getenv("CHEMCONDA_HOME_PATH", None)
    # CHEMCONDA_REMOTE_REPO
    remote_repo = os.getenv("CHEMCONDA_REMOTE_REPO", "https://repo.anaconda.com/miniconda")
    # CHEMCONDA_INSTALLER
    installer = os.getenv("CHEMCONDA_INSTALLER", "Miniconda3-py39_4.9.2-Linux-x86_64.sh")
    # CHEMCONDA_LOCAL_TMP
    download_dir = os.getenv("CHEMCONDA_DOWNLOAD_DIR", "/tmp")
    # CHEMCONDA_INSTALLER_PATH
    installer_path = os.getenv("CHEMCONDA_INSTALLER_PATH", os.path.join(download_dir, installer))

    def args_dict(self) -> dict:
        return {
            "CHEMCONDA_HOME_PATH": self._home_path,
            "CHEMCONDA_REMOTE_REPO": self.remote_repo,
            "CHEMCONDA_INSTALLER": self.installer,
            "CHEMCONDA_DOWNLOAD_DIR": self.download_dir,
            "CHEMCONDA_INSTALLER_PATH": self.installer_path,
        }

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
                cls._instance._home_path = cls._instance._home_path if 'CHEMCONDA_HOME_PATH' not in _config_cache else _config_cache['CHEMCONDA_HOME_PATH']
            else:
                # init a new ~/.config/chemconda/config.yaml with default params
                if not os.path.exists(os.path.dirname(CONFIG_FILE)):
                    # create parent folder for keeping CONFIG_FILE
                    os.makedirs(os.path.dirname(CONFIG_FILE))

                with open(CONFIG_FILE, 'w') as fw:
                    yaml.dump(cls._instance.args_dict(), fw, default_flow_style=False)

        return cls._instance

    @property
    def home_path(self):
        return self._home_path

    @home_path.setter
    def home_path(self, p):
        self._home_path = p
        _config_cache = self.args_dict

        # upload yaml in the CONFIG_FILE
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as stream:
                try:
                    _config_cache = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    raise exc

            _config_cache['CHEMCONDA_HOME_PATH'] = p

            with open(CONFIG_FILE, 'w') as fw:
                yaml.dump(_config_cache, fw, default_flow_style=False)