import os
import json
import shutil
import signal
import requests
import subprocess
import tarfile
from threading import Event
from glob import glob

import boto3
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

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

    conda_bin = 'bin/conda'
    if not config.home_path:
        console.print("CHEMCONDA_HOME_PATH has not been set.")
    else:
        conda_bin = os.path.join(config.home_path, "bin/conda")
        if not os.path.exists(conda_bin):
            console.print("CHEMCONDA_HOME_PATH({}) does not have any conda envs.".format(conda_bin))

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

    conda_bin = 'bin/conda'
    if not os.path.exists(config.home_path):
        console.print("CHEMCONDA_HOME_PATH does not exist.")
    else:
        conda_bin = os.path.join(config.home_path, "bin/conda")
        if not os.path.exists(conda_bin):
            console.print("CHEMCONDA_HOME_PATH({}) does not have any conda envs.".format(conda_bin))

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

def show_remote_info(envs, config=None, console=None):

    if not config:
        config = Config()

    if not console:
        console = Console()

    aws_profile = config.aws_profile
    remote_bucket = config.aws_s3_bucket
    
    if envs:
        # list all the available envs
        boto3.setup_default_session(profile_name=aws_profile)
        s3 = boto3.client('s3')
        
        objects_dict = dict()
        list_objects_resp = s3.list_objects_v2(Bucket=remote_bucket)
        if 'Contents' in list_objects_resp:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key", style='dim')
            table.add_column("LastModified", style="dim", width=12)
            table.add_column("Size(MB)", justify="right")
            table.add_column("StorageClass", justify="right")

            # list all the available envs
            boto3.setup_default_session(profile_name=aws_profile)
            s3 = boto3.client('s3')

            objects_dict = dict()
            list_objects_resp = s3.list_objects_v2(Bucket=remote_bucket)
            if "Contents" in list_objects_resp:
                for object_json in list_objects_resp['Contents']:
                    object_row = list(object_json.values())
                    print_row = []
                    print_row.append(object_row[0])
                    print_row.append(object_row[1].strftime("%m/%d/%Y, %H:%M:%S"))
                    print_row.append(str(format(object_row[3]/1048576.0, '.2f')))
                    print_row.append(object_row[4])
                    table.add_row(*print_row)

            console.print(table)
        else:
            console.print("No available environments found in remote repository.")

    else:
        
        # show aws profile with remote bucket name
        console.print("aws profile: {}".format(aws_profile))
        console.print("remote bucket: {}".format(remote_bucket))

def show_info(envs, config=None, console=None):
    
    if not config:
        config = Config()

    if not console:
        console = Console()

    if envs:
        # list all the available envs under the CHEMCONDA_HOME_PATH
        console.print("Available environments: ")
        env_names = [os.path.basename(dirpath) for dirpath in glob(os.path.join(config.home_path, 'envs/*'))]
        for env_name in env_names:
            console.print("- {}".format(env_name))
    else:
        console.print("Local configuration in ~/.config/chemconda/config.yaml: ")
        console.print(config.args_dict())

def fetch_conda_env(dst, src, auto_add_kernels=True, config=None, console=None):
    # expand user path to abspath
    dst = os.path.expanduser(dst)
    src = os.path.expanduser(src)

    if not config:
        config = Config()

    if not console:
        console = Console()

    console.print("Ready to untar a Miniconda3 under the {}".format(dst))
    if os.path.exists(os.path.join(dst, 'miniconda3')):
        console.print("CHEMCONDA_HOME_PATH {} has already existed.".format(config.home_path))
    
    # download and decompress to config.download_dir
    aws_profile = config.aws_profile
    remote_bucket = config.aws_s3_bucket

    boto3.setup_default_session(profile_name=aws_profile)
    s3 = boto3.client('s3')

    # try-to-download packaged file
    download_filepath = os.path.join(config.download_dir, src)
    with open(download_filepath, 'wb') as data:
        try:
            s3.download_fileobj(remote_bucket, src, data)
        except Exception as exc:
            raise(exc)
    
    # untar the package to dst path
    tar = tarfile.open(download_filepath)
    tar.extractall(path=dst)
    tar.close()

    # add kernels
    if auto_add_kernels:
        # search the config.home_path/envs/ folder to get all the potential kernels.
        env_names = [os.path.basename(dirpath) for dirpath in glob(os.path.join(dst, 'envs/*'))]
        console.print("Found {} kernels, start to restore...".format(len(env_names)))
        for env_name in env_names:
            console.print("Adding kernel {}".format(env_name))
            add_existed_kernel(env_name, config=config, console=console)
        console.print("All kernels have been added.")

    # update config.home_path
    if not config.home_path:
        # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
        config.home_path = dst
        config.installer = None
    else:
        if config.home_path != os.path.abspath(os.path.expanduser(dst)):
            # overwrite the CHEMCONDA_HOME_PATH in the ~/.chemconda/config.yaml file
            config.home_path = dst

def publish_conda_env(dst, src, config=None, console=None):
    # expand user path to abspath
    src = os.path.expanduser(src)

    if not config:
        config = Config()
    
    if not console:
        console = Console()

    console.print("Ready to upload the package: {}.".format(dst))
    if not os.path.exists(src):
        raise Exception("Miniconda3 does not exist in the path.".format(src))

    # download and decompress to config.download_dir
    aws_profile = config.aws_profile
    remote_bucket = config.aws_s3_bucket

    boto3.setup_default_session(profile_name=aws_profile)
    s3 = boto3.client('s3')

    # tar-and-upload the package
    tar_fname = dst
    if not tar_fname.endswith(".tar.gz"):
        tar_fname = '{}.tar.gz'.format(dst)

    # start tar-compressing
    tar_fpath = os.path.join("/tmp", tar_fname)
    console.print("Start tar compressing {}.".format(tar_fpath))
    tar = tarfile.open(tar_fpath, "w:gz")
    tar.add(src)
    tar.close()
    console.print("Successfully generated.")

    # start uploading 
    console.print("Start uploading tar file to {}...".format(tar_fname))
    with open(tar_fpath, 'rb') as data:
        s3.upload_fileobj(data, remote_bucket, tar_fname)
    console.print("Sucessfully uploaded.")

    # remove package tmp file if successfully uploaded
    os.remove(tar_fpath)
    if not os.path.exists(tar_fpath):
        console.print("Temp file cleared.")
    else:
        console.print("Failed to clear temp file {}.".format(tar_fpath))