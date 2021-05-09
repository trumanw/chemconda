import io

import click
from rich.console import Console

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
    help="the name of the conda env to be craeted.")
def cmd():
    """Setup a conda env as a new Jupyter kernel.
    """
    pass