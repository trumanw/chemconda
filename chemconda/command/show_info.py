import io

import click
from rich.console import Console

class RichHelpCommand(click.Command):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)

        example_source_code = """
    chemconda info
        """

        # customize the output
        sio = io.StringIO()
        console = Console(file=sio, force_terminal=True)
        console.print("\n[bold]Example: ", style="white")
        console.print(example_source_code, style="bold yellow")
        formatter.write(sio.getvalue())
        

@click.command(cls=RichHelpCommand)
def cmd():
    """Print help info on the terminal screen.
    """
    example_source_code = """
    chemconda info
        """
    console = Console(force_terminal=True)
    console.print("\n[bold]Example: ", style="white")
    console.print(example_source_code, style="bold yellow")