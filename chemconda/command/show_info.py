import io
import os
import click
from rich.console import Console

from ..config import Config
from ..utils import show_remote_info, show_info

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda info
    chemconda info --envs
    chemconda info --envs -r
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())


@click.command(cls=RichHelpCommand)
@click.option("-e", "--envs", is_flag=True, prompt=False,
    help="show available environments list.")
@click.option("-r", "--remote", is_flag=True, prompt=False, 
    help="show remote info.")
def cmd(envs, remote):
    """Print help info on the terminal screen.
    """

    # console init
    console = Console()
    # load config
    config = Config()

    if not config.home_path:
        console.print("CHEMCONDA_HOME_PATH has not been set.")
    else:
        if not os.path.exists(config.home_path):
            console.print("CHEMCONDA_HOME_PATH does not exist.")
        else:
            conda_bin = os.path.join(config.home_path, "bin/conda")
            if not os.path.exists(conda_bin):
                console.print("CHEMCONDA_HOME_PATH({}) does not have any conda envs.".format(conda_bin))

    if remote:
        # show remote info 
        show_remote_info(envs)
    else:
        # show local installed info
        show_info(envs)