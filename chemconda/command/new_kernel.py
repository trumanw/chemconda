import io

import click
from rich.console import Console

from ..config import Config
from ..utils import install_new_kernel

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda new -n aidd
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())

@click.command(cls=RichHelpCommand)
@click.option("-n", "--name", required=True, prompt=True, type=str,
    help="the name of the conda env to be created.")
@click.option("-v", "--python-ver", required=False, prompt=True, type=str, default="3.8",
    help="the version of the python to be pre-installed in the new conda env.")
@click.option("--new-kernel", is_flag=True, prompt=True,
    help="add the conda env as a new Jupyter kernel.")
@click.option("--new-condarc", is_flag=True, prompt=True, 
    help="create a new ~/.condarc or overwrite if it exists.")
def cmd(name, python_ver, new_kernel, new_condarc):
    """Setup a conda env as a new Jupyter kernel.
    """

    # console init 
    console = Console()
    # load config   
    config = Config()

    install_new_kernel(name, python_ver, new_kernel, new_condarc, config=config, console=console)