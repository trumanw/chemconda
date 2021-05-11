import os
import signal
import requests
import subprocess
from threading import Event

from rich.console import Console
from rich.progress import Progress

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

def rich_exec_subprocess(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = sp.stdout.readline().rstrip()
        if not line:
            break
        yield line

def install_packages(env_name, package_names, add_channels=None, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()
    
    console.print("Start installing packages...")
    # install necessary packages in the new conda
    new_conda_bin = os.path.join(config.home_path, "bin/conda")
    
    if not isinstance(package_names, list):
        raise Exception("package_names shoud be a list")
    package_lines = " ".join(package_names)

    pkg_install_cmd = "{} install --name {} {} -y".format(new_conda_bin, env_name, package_lines)
    if isinstance(add_channels, list) and len(add_channels) > 0:
        channel_lines = " -c ".join(add_channels)
        pkg_install_cmd = pkg_install_cmd + " -c {}".format(channel_lines)
    
    #TODO: logger.info
    console.print(pkg_install_cmd)
    console.print(exec_subprocess(pkg_install_cmd))
    #FIXME: cannot catch the realtime conda installing stdout...
    # [console.print(line) for line in rich_exec_subprocess(pkg_install_cmd)]
        

def install_conda_env(destination, binary=None, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()

    console.print("Update config...")
    des_abspath = os.path.abspath(os.path.expanduser(destination))
    if not config.home_path:
        # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
        config.home_path = des_abspath
        config.installer = binary
    else:
        if config.home_path != os.path.abspath(os.path.expanduser(destination)):
            # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
            config.home_path = des_abspath

    console.print("Config completed:")
    console.print(config.args_dict())
            
    console.print("Setup Miniconda...")
    # validate CHEMCONDA_HOME_PATH is consistent to the config.home_path
    if not os.path.exists(config.home_path):
        # install Miniconda3 from remote repository
        conda_download_url = os.path.join(config.remote_repo, config.installer)

        console.print("Cannot find Miniconda installer, downloading from {}".format(conda_download_url))
        res = requests.get(conda_download_url, stream=True, allow_redirects=True)
        total_length = res.headers.get('content-length')

        done_event = Event()
        def handle_sigint(signum, frame):
            done_event.set()
        signal.signal(signal.SIGINT, handle_sigint)
        
        with open(config.installer_path, 'wb') as fw:
            if total_length is None: # no content length header
                    fw.write(res.content)
            else:
                dl = 0
                total_length = int(total_length)
                with Progress() as progress:
                    download_task = progress.add_task("[green]Downloading...", total=total_length)
                    for data in res.iter_content(chunk_size=32768):
                        fw.write(data)
                        progress.update(download_task, advance=len(data))
                        if done_event.is_set():
                            return

        console.print("Downloading completed : {}".format(config.installer_path))

        console.print("Installing {}...".format(config.installer))
        if os.path.isfile(config.installer_path):
            # ensure bash installed
            os.system("bash {} -b -p {}".format(config.installer_path, config.home_path))
        console.print("Installing completed.")

    # show the installed Minconda3 home path
    console.print("Setup completed: conda installed at {}".format(config.home_path), style="bold white")

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
        with open(os.path.expanduser("~/.condarc"), 'w') as fw:
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
