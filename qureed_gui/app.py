import subprocess
import sys
import os
import pathlib
import click


@click.group()
def cli():
    pass

@cli.command()
@click.argument('name', required=True)
def create_project(name):
    from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

    LMH = LogicModuleHandler()
    PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
    cwd = pathlib.Path.cwd() 
    if not click.confirm(f'Do you want to create project here: ({cwd}/name)?'):
        click.echo('Aborting!')
        return
    click.echo("Creating Project")
    PM.new_project(f"{cwd}/{name}")

@cli.command()
def test():
    """
    Tests modules in current directory
    """
    

@cli.command()
@click.option('--dev', is_flag=True, help="Run in development mode.")
def run(dev):
    click.echo("Running QuReedGui")
    here = pathlib.Path(__file__).parent.resolve()
    main_path = here / "main.py"

    user_cwd = pathlib.Path.cwd()

    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"
    env["QUREED_CWD"] = str(user_cwd)
    env["QUREED_PY_EXE"] = str(sys.executable)


    subprocess.run(
        ["flet", "run", "--web", str(main_path)],
        env=env,
        cwd=pathlib.Path.cwd()
    )

if __name__ == '__main__':
    cli()
