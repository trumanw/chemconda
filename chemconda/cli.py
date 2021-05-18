import uuid
import click

from chemconda import __version__
from chemconda.command import import_conda, install_conda, \
    new_kernel, \
    install_packages, \
    show_info, \
    rm_kernel

@click.group()
@click.version_option(__version__, "--version")
@click.pass_context
def cli(ctx):
    """Chemconda"""
    # generate unique handler for each execution
    hnd = uuid.uuid4().hex
    ctx.obj = {
        "handle": hnd
    }

# register sub-commands here:
cli.add_command(install_conda.cmd, "setup")
cli.add_command(show_info.cmd, "info")
cli.add_command(new_kernel.cmd, "new")
cli.add_command(install_packages.cmd, "add")
cli.add_command(rm_kernel.cmd, "rm")
cli.add_command(import_conda.cmd, "imp")