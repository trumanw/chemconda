import os
import requests
import subprocess

from rich.console import Console

from .config import Config

def exec_subprocess(cmd, is_split=False):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = sp.communicate()
    
    if out:
        if not is_split:
            return out.decode()
        else:
            return out.decode().split()
    
    if err:
        raise(Exception(err.decode()))

def install_packages(env_name, package_names, add_channels=None, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()
    
    # install necessary packages in the new conda
    new_conda_bin = os.path.join(config.home_path, "bin/conda")
    
    if not isinstance(package_names, list):
        raise Exception("package_names shoud be a list")
    package_lines = " ".join(package_names)

    installer = "{} install --name {} {} -y".format(new_conda_bin, env_name, package_lines)
    if isinstance(add_channels, list) and len(add_channels) > 0:
        channel_lines = " -c ".join(add_channels)
        installer = installer + " -c {}".format(channel_lines)
    
    #TODO: logger.info
    console.print(installer)
    
    return exec_subprocess(installer)

def install_conda_env(des, ver=None, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()

    if not config.home_path:
        # prepare for another new intallation
        config.home_path = os.path.abspath(os.path.expanduser(des))
        config.installer = ver
    else:
        if config.home_path != os.path.abspath(os.path.expanduser(des)):
            # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
            #TODO: update the config file.
            console.print("CHEMCONDA_HOME_PATH in the file ~/.chemconda/config.yaml is updated.")
            config.home_path = os.path.abspath(os.path.expanduser(des))

    # validate CHEMCONDA_HOME_PATH is consistent to the config.home_path
    if not os.path.exists(config.home_path):
        # install Miniconda3 from remote repository
        conda_download_url = os.path.join(config.remote_repo, config.installer)
        conda_download_dir = os.path.join(config.download_dir, config.installer)

        res = requests.get(conda_download_url, allow_redirects=True)
        with open(config.installer_path, 'wb') as fw:
            fw.write(res.content)

        if os.path.isfile(config.installer_path):
            # ensure bash installed
            console.print("Installing {} ...".format(config.installer))
            os.system("bash {} -b -p {}".format(config.installer_path, config.home_path))

        # show the installed Minconda3 home path
        console.print(config.home_path)
    else:
        console.print("{} has been installed.".format(config.home_path))

def install_new_kernel(env_name, python_ver, new_kernel, new_condarc, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()

    if not os.path.exists(config.home_path):
        console.print("CHEMCONDA_HOME_PATH cannot be empty.")

    conda_bin = os.path.join(config.home_path, "bin/conda")
    if not os.path.exists(conda_bin):
        console.print("CHEMCONDA_HOME_PATH({}) does not exist.".format(conda_bin))

    # update ~/.condarc file if is_override channels
    if new_condarc:
        condarc_raw = """channels:
  - conda-forge
  - salilab
  - omnia
  - pytorch
  - anaconda
  - defaults
"""
        with open("~/.condarc", 'w') as fw:
            fw.write(condarc_raw)
    
    # create a new conda env if it does not exist
    if not os.path.exists(os.path.join(config.home_path, 'envs/{}'.format(env_name))):
        # create a new conda env
        os.system("{} create -n {} python={} -y".format(
            conda_bin, 
            env_name, 
            python_ver))

        # install necessary packages to the new conda env
        os.system("{} install --name {} ipython ipykernel -y".format(conda_bin, env_name))
    
    # add conda env as a new kernel
    if new_kernel:
        ipython_bin = os.path.join(config.home_path, "envs/{}/bin/ipython".format(env_name))
        if not os.path.exists(ipython_bin):
            os.system("{} install --name {} ipython ipykernel -y".format(conda_bin, env_name))
        
        os.system('{} kernel install --name "{}" --user'.format(ipython_bin, env_name))

    # additional sidecar packages for Jupyter Notebook/Lab users
    install_packages(
        package_names=['jedi=0.18'], 
        env_name=env_name, 
        add_channels=['conda-forge'],
        config=config,
        console=console)
    # to overwrite the jedi=0.17 installed in the jupyter lab(if existed)
    # ...
