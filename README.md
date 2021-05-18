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

### 3. Import a existed conda env.

Sometimes we can create and setup an initialized conda env on a NAS-like hardware driver once. So that others can simply import the initializesd conda env directly from hardware driver through:

```shell
chemconda imp -s /path-to-nas/miniconda3 -d /root/miniconda3
```

The command above would do two things:
- copy-and-paste the whole directory from `-d` to `-s` path, if `-d` is a valid conda env root directory.
- scann the `./envs/` path under the `-d` directory, and automatically add found kernels to the jupyter kernelspec list.

### 4. Install Python package to the specific conda env

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

### 5. Restore conda kernel

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

### 6. Remove conda kernel

Remove conda env from Jupyter kernelspec list:

```shell
chemconda rm -n env_name
```

### 7. Remote chemconda repository on AWS S3:

You can quickly setup a bucket as a chemconda repo, tar your whole miniconda3 folder into a tar.gz package and upload a specific S3 bucket. Then using the sub-cmd below to see the remote available miniconda environments:

```shell
chemconda show --envs -r
```
which the `-r` means the `-remote`, you can also use the same cmd without `-r` to check the added local miniconda envs.

Next, you can also pull, extract and build a new Miniconda3 environment ready for Jupyter kernels through the sub-cmd below:

```shell
chemconda pull -d /root -s miniconda3-v0.0.tar.gz
```

while, the sub-cmd would download the `miniconda3-v0.0.tar.gz` from remote repo and setup a Miniconda3 to the path `/root/miniconda3`. You can also see the kernels of the miniconda envs appeared in the jupyter kernelspecs.

*NOTICE*
You should take care of setting the AWS credential and AWS S3 by yourself, for more details please check:
- AWS Credential: [Configuration and credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- AWS S3: [Amazon S3 mainpage](https://aws.amazon.com/s3/)

The credential usage is prefered to be picked by AWS_PROFILE, which could be set by ENV VAR `CHEMCONDA_AWS_PROFILE` or inside ~/.config/chemconda/config.yaml. Also, you can specify the AWS Bucket through ENV VAR `CHEMCONDA_AWS_S3_BUCKET` or in the ~/.config/chemconda/config.yaml file.

### 7. (Upcoming) New a conda env from environment.yaml (from chemconda templates library)

`chemconda` has created and tested various of conda templates under the `./template` directory. The manifest of the templates are listed below:

## Environment variables as settings

There are several pre-config environment variables which could control the actions of the conda environment setup:

```python
# ENV VARS
# - CHEMCONDA_HOME_PATH: the target miniconda installing location, 
#       default: /home/vintage/miniconda3'
# - CHEMCONDA_INSTALLER: the name of the Miniconda installer,
#       default: Miniconda3-py39_4.9.2-Linux-x86_64.sh
# - CHEMCONDA_REMOTE_REPO: the prefix URI of the Miniconda installer,
#       default: https://repo.anaconda.com/miniconda'
# - CHEMCONDA_DOWNLOAD_DIR: the local directory used for keeping downloading installer,
#       default: /tmp
# - CHEMCONDA_AWS_PROFILE: the AWS credential profile to access to the remote repository on AWS S3.
# - CHEMCONDA_AWS_S3_BUCKET: the AWS S3 bucket used for keeping packed Miniconda3 as a remote repo.
```

## Coming features:
- Dotenv with better usage of ENV VAR loading.