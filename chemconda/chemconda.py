import os
import requests
import subprocess

from .config import Config

# Constants
# ENV VARS
config = Config()

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

def install_miniconda(installed_dir=config.home_path):
    is_from_remote = True

    # install miniconda
    if not os.path.exists(config.home_path):

        if is_from_remote:
            # download installer from remote
            conda_download_url = os.path.join(config.remote_repo, config.installer)
            conda_download_dir = os.path.join(config.download_dir, config.installer)

            # download Miniconda installer
            res = requests.get(conda_download_url, allow_redirects=True)
            with open(config.installer_path, 'wb') as fw:
                fw.write(res.content)

        if os.path.isfile(config.installer_path):
            # install miniconda from installation shell
            os.system("bash {} -b -p {}".format(config.installer_path, config.home_path))
    else:
        #TODO: logger.info
        print("{} has already installed".format(config.home_path))
        
def prepare_miniconda_env(env_name="aidd", python_ver="3.8", is_new_kernel=False, is_override_condarc=False):
    
    # install necessary packages in the new conda
    new_conda_bin = os.path.join(config.home_path, "bin/conda")
    
    # update ~/.condarc file
    if is_override_condarc:
        #TODO: load content from a outside file
        condarc_raw = """channels:
  - conda-forge
  - salilab
  - omnia
  - pytorch
  - anaconda
  - defaults
"""
        with open('~/.condarc', 'w') as fw:
            fw.write(condarc_raw)
        
    # create a new conda env if it does not exist
    if not os.path.exists(os.path.join(config.home_path, 'envs/{}'.format(env_name))):
        # create a new conda env
        os.system("{} create -n {} python={} -y".format(
            new_conda_bin, 
            env_name, 
            python_ver))
    
        # install necesary packages to the new conda env
        os.system("{} install --name {} ipython ipykernel -y".format(new_conda_bin, env_name))
    
    # add kernel
    if is_new_kernel:
        ipython_bin = os.path.join(config.home_path, "envs/{}/bin/ipython".format(env_name))
        if not os.path.exists(ipython_bin):
            os.system("{} install --name {} ipython ipykernel -y".format(new_conda_bin, env_name))
            
        os.system('{} kernel install --name "{}" --user'.format(ipython_bin, env_name))

    # additional sidecar package
    install_package(package_names=['jedi=0.18'], env_name=env_name, add_channels=['conda-forge'])
    # to overwrite the jedi=0.17 installed in the jupyter lab(if existed)
    # ...

def remove_miniconda_env(env_name="aidd"):
    
    # check if the ipykernel exists
    kernels_output =  exec_subprocess("jupyter kernelspec list")
    kernels_dict = {}
    for k_l in kernels_output.split('\n')[1:-1]:
        k_l_slice = k_l.split()
        # which 0th is the name of the kernel, and 1st is the location
        kernels_dict[k_l_slice[0]] = k_l_slice[1]
    
    #TODO: logger.info
    print("detected kernels : ", kernels_dict)
        
    if env_name in kernels_dict:
        kernel_removed_output = exec_subprocess("jupyter kernelspec remove {} -f".format(env_name))
    
    # check if the env exists
    new_conda_bin = os.path.join(config.home_path, "bin/conda")
    if os.path.exists(os.path.join(config.home_path, "envs/{}".format(env_name))):
        env_removed_output = exec_subprocess("{} remove -n {} --all -y".format(new_conda_bin, env_name))
    
    #TODO: logger.info
    print(env_removed_output)

def install_package(package_names, env_name, add_channels=None):
    
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
    print(installer)
    
    return exec_subprocess(installer)