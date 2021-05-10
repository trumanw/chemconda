# chemconda
Install Conda and add ipykernel easily on Jupyter Notebook/Lab.

## Usage (cmd)

### 1. Install a new miniconda

```shell
pip install -q chemconda
```

After installing completed, we can install a new miniconda through the command below:

```shell
chemconda setup \
    -d /root/miniconda3 \
    -b Miniconda3-py39_4.9.2-Linux-x86_64.sh
```

which the sub-command `setup` accepts a directory path and installs the veresion `Miniconda3-py39_4.9.2-Linux-x86_64` from the [Miniconda](https://repo.anaconda.com/miniconda/) repository website. Also you can change the `-v` to be any other version listed on the repository website.

### 2. Create a new conda env and add to the jupyter kernels.

Before we start to create any new conda env, please make sure the environment variable `CHEMCONDA_HOME_PATH` is correctly set to the miniconda installing path above. Otherwise, you should move to the installed miniconda root path and execute the lines below to reset the `CHEMCONDA_HOME_PATH`:

```shell
cd /root/miniconda3
chemconda setup -d ./
```

After `CHEMCONDA_HOME_PATH` is correctly setup, run the lines below to create a new conda env:

```shell
chemconda new -n aidd
```

The sub-commmand `new` accepts one name after `-n` and create a new conda env under the `[CHEMCONDA_HOME_PATH]\env` path.

### 3. Install Python package to the specific conda env

Before install any Python package, please make sure again the `CHEMCONDA_HOME_PATH` is correctly set:

```shell
echo $CHEMCONDA_HOME_PATH
```

Here I try to install latest `rdkit` and `numpy` packages from `conda-forge` channel:

```shell
chemconda add \
    -n env_name \
    -p rdkit \
    -p numpy \
    -c conda-forge
```

which the statement equals the command below:

```shell
conda install rdkit numpy --name env_name -c conda-forge -y
```

### 4. Restore conda kernel

Given the situation of the whole instance on Cloud is recovered and restarted with mountable HD driver, we can move the rootpath of miniconda installed on the moutable HD driver and run the lines below to re-add the conda env to the Jupyter kernelspec list:

```shell
pip install chemconda
cd [CHEMCONDA_HOME_PATH]
chemconda setup -d ./
chemconda new -n env_name
```

In case, you can also list all the current available kernels to ensure the `aidd` is listed:

```
jupyter kernelspec list
```

## Environment variables as settings

There are several pre-config environment variables which could control the actions of the conda environment setup:

```python
# ENV VARS
# - CHEMCONDA_INSTALL_PATH: the target miniconda installing location, 
#       default: /home/vintage/miniconda3'
# - CHEMCONDA_BINARY: the name of the Miniconda installer,
#       default: Miniconda3-py39_4.9.2-Linux-x86_64.sh
# - CHEMCONDA_PREFIX_URI: the prefix URI of the Miniconda installer,
#       default: https://repo.anaconda.com/miniconda'
# - CHEMCONDA_DOWNLOAD_DIR: the local directory used for keeping downloading installer,
#       default: /tmp
```

## Coming features:
- Rich command line interface.
- Dotenv with better usage of ENV VAR loading.