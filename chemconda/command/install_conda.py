import io
import os
import requests

import click
from rich.console import Console

from ..config import Config
from ..utils import install_conda_env

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda setup -d /root/miniconda3 -v Miniconda3-py39_4.9.2-Linux-x86_64
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())
        
@click.command(cls=RichHelpCommand)
@click.option("-d", "--des", required=True, prompt=True, type=str, 
    help="destination path of installing miniconda.")
@click.option("-v", "--ver", required=False, prompt=False, type=str,
    default="Miniconda3-py39_4.9.2-Linux-x86_64",
    help="the name of the remote miniconda package to be installed.")
def cmd(des, ver):
    """Install a new conda with a specific CHEMCONDA_HOME_PATH.
    """
    # console init 
    console = Console()
    # load config singleton    
    config = Config()

    install_conda_env(des, ver, config=config, console=console)