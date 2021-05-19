import io

import click
from click.termui import prompt
from rich.console import Console

from ..config import Config
from ..utils import publish_conda_env

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda push -d miniconda3-v0.0 -s ./miniconda3
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())
        
@click.command(cls=RichHelpCommand)
@click.option("-d", "--dst", required=True, prompt=True, type=str, 
    help="destination path of installing miniconda.")
@click.option("-s", "--src", required=False, prompt=False, type=str,
    default="Miniconda3-py39_4.9.2-Linux-x86_64.sh",
    help="the name of the remote miniconda package to be installed.")
def cmd(dst, src):
    """Fetch a new conda env from the remote repository and setup CHEMCONDA_HOME_PATH.
    """
    # console init 
    console = Console()
    # load config singleton    
    config = Config()

    publish_conda_env(dst, src, auto_add_kernels=True, config=config, console=console)