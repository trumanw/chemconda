# chemconda
Install Conda and add ipykernel easily on Jupyter Notebook/Lab.

## Usage

On your Jupyter Notebook, run the following code:

```python
!pip install -q chemconda

import os
os.environ['CHEMCONDA_INSTALL_PATH'] = '/root/miniconda3'
```

Then you can install miniconda to the `CHEMCONDA_INSTALL_PATH` location:
```python
import chemconda
chemconda.install_miniconda()
```

After the miniconda installed, you can create an conda env and add to ipykernel:

```python
import chemconda
chemconda.prepare_miniconda_env(env_name="aidd", is_new_kernel=True)
```

Also, you can permantly delete a conda env by:

```python
import chemconda
chemconda.remove_miniconda_env(env_name="aidd")
```

After the conda environment has been prepared, you can using the lines below to install packages to target environment:

```python
import chemconda
# install rdkit and numpy to aidd env 
chemconda.install_package(['rdkit', 'numpy'], 'aidd')
```

> NOTICE: after restart the kernel of Jupyter or refresh the webpage, you can also "Select Kernel" added previously. 

If the server restarted and you want to restore the kernel, you can open a base environment Python env and re-add the ipykernel by

```python
!pip install -q chemconda

## make sure adding the environment before anything else
import os
os.environ['CHEMCONDA_INSTALL_PATH'] = '/root/miniconda3'

import chemconda
## skip installation if it has already existed
chemconda.install_miniconda()
## re-add the ipykernel to the jupyter
chemconda.prepare_miniconda_env(env_name="aidd", is_new_kernel=True)
```

Then you can see the kernel is optional:

```
!jupyter kernelspec list
```

which the output lines have the `env_name` listed inside.

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