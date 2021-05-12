import io
import os

import click
from rich.console import Console

from ..config import Config
from ..utils import install_packages

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda add -n env_name -p rdkit -c conda-forge
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())

@click.command(cls=RichHelpCommand)
@click.option("-n", "--name", required=True, prompt=True, type=str,
    help="the name of the conda env to be updated.")
@click.option("-p", "--package", required=True, prompt=True, type=str, multiple=True,
    help="the conda package name.")
@click.option("-c", "--channel", required=False, prompt=False, type=str, multiple=True,
    help="the conda channel name.")
@click.option("--fast", is_flag=True, prompt=False, 
    help="using mamba(faster than conda) to install")
def cmd(name, package, channel, fast):
    """Install conda packages to the environment.
    """
    
    # console init
    console = Console()
    # load config
    config = Config()

    if not os.path.exists(config.home_path):
        console.print("CHEMCONDA_HOME_PATH cannot be empty.")

    conda_bin = os.path.join(config.home_path, "bin/conda")
    if not os.path.exists(conda_bin):
        console.print("CHEMCONDA_HOME_PATH({}) does not exist.".format(conda_bin))
        
    install_packages(
        env_name=name,
        package_names=list(package),
        add_channels=list(channel),
        fast_mode=fast,
        config=config,
        console=console)