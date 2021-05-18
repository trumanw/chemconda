import os
import json
import shutil
import signal
import requests
import subprocess
from threading import Event
from glob import glob

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

def install_packages(env_name, package_names, fast_mode=False, add_channels=None, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()
    
    console.print("Start installing packages...")
    # install necessary packages in the new conda
    if fast_mode:
        new_conda_bin = os.path.join(config.home_path, "bin/mamba")
    else:
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
        

def install_conda_env(destination, binary=None, auto_add_kernels=True, config=None, console=None):

    destination = os.path.expanduser(destination)

    if not config:
        config = Config()

    if not console:
        console = Console()

    console.print("Update config...")
    des_abspath = os.path.abspath(destination)
    if not config.home_path:
        # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
        config.home_path = des_abspath
        config.installer = binary
    else:
        if config.home_path != os.path.abspath(destination):
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

        console.print("Start installing base dependencies...")
        # install sidecar in the base env
        install_packages(
            package_names=['jedi=0.18', 'mamba'], 
            env_name='base', 
            add_channels=['conda-forge'],
            config=config,
            console=console)
        console.print("Installing completed.")

        # show the installed Minconda3 home path
        console.print("Setup completed: conda installed at {}".format(config.home_path), style="bold white")
    else:
        if auto_add_kernels:
            # search the config.home_path/envs/ folder to get all the potential kernels.
            env_names = [os.path.basename(dirpath) for dirpath in glob(os.path.join(config.home_path, 'envs/*'))]
            console.print("Found {} kernels, start to restore...".format(len(env_names)))
            for env_name in env_names:
                console.print("Adding kernel {}".format(env_name))
                add_existed_kernel(env_name, config=config, console=console)
            console.print("All kernels have been added.")

def remove_kernel(env_name, config=None, console=None):

    if not config:
        config = Config()
    
    if not console:
        console = Console()

    if not os.path.exists(config.home_path):
        console.print("CHEMCONDA_HOME_PATH cannot be empty.")

    conda_bin = os.path.join(config.home_path, "bin/conda")
    if not os.path.exists(conda_bin):
        console.print("CHEMCONDA_HOME_PATH({}) does not exist.".format(conda_bin))

    # check if the ipykernel exists
    kernels_output =  exec_subprocess("jupyter kernelspec list")
    kernels_dict = {}
    for k_l in kernels_output.split('\n')[1:-1]:
        k_l_slice = k_l.split()
        # which 0th is the name of the kernel, and 1st is the location
        kernels_dict[k_l_slice[0]] = k_l_slice[1]
    
    #TODO: logger.info
    console.print("detected kernels : ", kernels_dict)
        
    if env_name in kernels_dict:
        kernel_removed_output = exec_subprocess("jupyter kernelspec remove {} -f".format(env_name))
    console.print(kernel_removed_output)
    
    # check if the env exists
    if os.path.exists(os.path.join(config.home_path, "envs/{}".format(env_name))):
        env_removed_output = exec_subprocess("{} remove -n {} --all -y".format(conda_bin, env_name))
    
    #TODO: logger.info
    console.print(env_removed_output)

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
  - pytorch
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
    
        console.print("Start installing base dependencies in the {}...".format(env_name))
        # additional sidecar packages for Jupyter Notebook/Lab users
        install_packages(
            package_names=['jedi=0.18', 'mamba'], 
            env_name=env_name, 
            add_channels=['conda-forge'],
            config=config,
            console=console)

    # add conda env as a new kernel
    if new_kernel:
        console.print("Start adding kernel {} to jupyter kernelspec list...".format(env_name))
        add_existed_kernel(env_name, config=config, console=console)
        console.print("Kernel {} added.".format(env_name))

    console.print("Setup completed.")

def add_existed_kernel(env_name, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()

    if not os.path.exists(config.home_path):
        console.print("CHEMCONDA_HOME_PATH cannot be empty.")

    conda_bin = os.path.join(config.home_path, "bin/conda")
    if not os.path.exists(conda_bin):
        console.print("CHEMCONDA_HOME_PATH({}) does not exist.".format(conda_bin))

    ipython_bin = os.path.join(config.home_path, "envs/{}/bin/ipython".format(env_name))
    if not os.path.exists(ipython_bin):
        os.system("{} install --name {} ipython ipykernel -y".format(conda_bin, env_name))
    
    os.system('{} kernel install --name "{}" --user'.format(ipython_bin, env_name))

    # add env args in the kernel.json
    kernel_file = os.path.join(
        os.path.expanduser("~/.local/share/jupyter/kernels"), "{}/kernel.json".format(env_name))
    if os.path.isfile(kernel_file):
        # processing update env
        with open(kernel_file) as f:
            kernel_dict = json.load(f)
        if 'env' not in kernel_dict:
            kernel_dict['env'] = {}
        env_bin_dir = os.path.join(config.home_path, "envs/{}/bin".format(env_name))
        kernel_dict['env']['PATH'] = os.environ['PATH']+":{}".format(env_bin_dir)

        with open(kernel_file, 'w') as fw:
            json.dump(kernel_dict, fw)

    else:
        raise Exception("failed to create a kernelspec in the jupyter.")

def import_conda_env(dst, src, auto_add_kernels=True, config=None, console=None):

    # expand user path to abspath
    dst = os.path.expanduser(dst)
    src = os.path.expanduser(src)

    if not config:
        config = Config()

    if not console:
        console = Console()

    if os.path.exists(dst):
        console.print("CHEMCONDA_HOME_PATH {} has already existed.".format(config.home_path))

    # conda_bin = os.path.join(config.home_path, "bin/conda")
    # if not os.path.exists(conda_bin):
        # console.print("CHEMCONDA_HOME_PATH({}) does not exist.".format(conda_bin))

    dst_conda_bin = os.path.join(src, "bin/conda") 
    if not os.path.exists(dst_conda_bin):
        console.print("Input dst path {} missing bin/conda under its root directory".format(src))

    # move the dst conda env to config.home_path
    dst_copied = shutil.copytree(src, dst)

    # add kernels
    if auto_add_kernels:
        # search the config.home_path/envs/ folder to get all the potential kernels.
        env_names = [os.path.basename(dirpath) for dirpath in glob(os.path.join(dst_copied, 'envs/*'))]
        console.print("Found {} kernels, start to restore...".format(len(env_names)))
        for env_name in env_names:
            console.print("Adding kernel {}".format(env_name))
            add_existed_kernel(env_name, config=config, console=console)
        console.print("All kernels have been added.")

    # update config.home_path
    if not config.home_path:
        # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
        config.home_path = dst_copied
        config.installer = None
    else:
        if config.home_path != os.path.abspath(os.path.expanduser(dst_copied)):
            # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
            config.home_path = dst_copied