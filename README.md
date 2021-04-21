# chemconda
Install Conda and add ipykernel easily on Jupyter Notebook/Lab.

## Usage

> **TLDR**: Check the [example notebook here](https://colab.research.google.com/drive/1c_RGCgQeLHVXlF44LyOFjfUW32CmG6BP)!)

On your Jupyter Notebook, run the following code:

```python
!pip install -q medconda

import medconda
medconda.install_miniconda()
```

After the miniconda installed, you can create an conda env and add to ipykernel:

```python
import medconda
medconda.prepare_miniconda_env(env_name="aidd", is_new_kernel=True)
```

Also, you can permantly delete a conda env by:

```python
import medconda
medconda.remove_miniconda_env(env_name="aidd")
```

After the conda environment has been prepared, you can using the lines below to install packages to target environment:

```python
import medconda
# install rdkit and numpy to aidd env 
medconda.install_package(['rdkit', 'numpy'], 'aidd')
```

> NOTICE: after restart the kernel of Jupyter or refresh the webpage, you can also "Select Kernel" added previously. 