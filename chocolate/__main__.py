import json
import time
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from .path import Path
from . import project_manager as prj

console = Console()


def dict_to_table(data, *args):
    table = Table(show_header=False)
    for key, value in data.items():
        table.add_row(str(key), str(value))
    return table


def ensure_project():
    project = prj.get_config()
    if not project:
        console.print(
            '[black on red]No project found. Please create a project first.[/]')
        quit(1)
    return project


def main():
    parser = argparse.ArgumentParser(description="Chocolate Project Manager.")
    parser.add_argument("action", type=str, help="Action")
    parser.add_argument('-n', '--name', help='Name of the project.')
    parser.add_argument("-p", "--parent", help="Project path (optional).")
    parser.add_argument("-m", "--main", type=str, help="Main file name.")
    parser.add_argument("pkgs", nargs="*",
                        help="Raw input after 'add' action", default=[])

    args = parser.parse_args()

    if args.action == 'new':
        if prj.get_config():
            console.print(
                '[black on red]You can\'t create a new project, .chocolate already exists.')
            quit(1)
        if not args.main or not args.name:
            console.print('[black on red]Missing arguments.')
            quit(1)
        console.print('Creating a new project.')
        prj.establish_project(args.name, args.main, '')
        console.print('Project created successfully.')

    elif args.action == 'run':
        project = ensure_project()
        console.print(f'[yellow]Initializing environment variables.')
        env = project['run', 'env']
        console.print(f'[yellow]Initializing flags.')
        flags = project['run', 'flags']
        console.print(f'[yellow]Setting up venv.')
        venv = prj.VenvManager('.venv')
        console.print(f'[green]Running {project["run"]["startfile"]}.')
        start = time.time()
        txt = f'[on green]OUTPUT OF {project["run", "startfile"]}'
        console.print(
            txt+'.'*(console.width-len(txt)+2))
        try:
            venv.run(project['run', 'startfile'], flags, env)
        except Exception as err:
            txt = f'[on red]App closed. [{time.time() - start:.2f}s]'
            console.print(
                txt+'.'*(console.width-len(txt)))
            console.print(err)
        else:
            txt = f'[on green]App closed. [{time.time() - start:.2f}s]'
            console.print(
                txt+'.'*(console.width-len(txt)))

    elif args.action == 'add':
        ensure_project()
        raw_project = json.loads(~Path()['.chocolate'])
        console.print(f'[yellow]Installing packages.')
        with Progress(
            SpinnerColumn(),  # Spinning animation
            BarColumn(),      # Progress bar
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("Processing...", total=len(args.pkgs))
            venv = prj.VenvManager('.venv')
            for pkg in args.pkgs:
                venv.install(pkg)
                progress.advance(task)
                if pkg not in raw_project['requirements']:
                    raw_project['requirements'].append(pkg)
            Path()['.chocolate'] = raw_project
        console.print(f'[green]Installed all packages successfully.')

    elif args.action == 'reinstall':
        raw_project = json.loads(~Path()['.chocolate'])
        console.print(f'[yellow]Reinstalling all packages.')
        with Progress(
            SpinnerColumn(),  # Spinning animation
            BarColumn(),      # Progress bar
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task(
                "Processing...", total=len(raw_project['requirements']))
            venv = prj.VenvManager('.venv')
            for pkg in raw_project['requirements']:
                venv.install(pkg)
                progress.advance(task)
        console.print(f'[green]All packages installed successfully.')

    elif args.action == 'env':
        project = ensure_project()
        if args.pkgs[0] == 'get':
            tbl = dict_to_table(project['run', 'env'])
            console.print(tbl)
        elif args.pkgs[0] == 'rem':
            raw_project = json.loads(~Path()['.chocolate'])
            console.print('[green]Removing env keys')
            for i in args.pkgs[1:]:
                raw_project['run']['env'].pop(i)
                console.print(f'[red]Removed {i}.')
            Path()['.chocolate'] = raw_project
        else:
            raw_project = json.loads(~Path()['.chocolate'])
            console.print('[green]Adding env.')
            for i in args.pkgs:
                i = i.split('=', 1)
                if i[0] in ['get', 'rem']:
                    console.print(f'[red]You cannot name your env key {i}')
                    quit(1)
                console.print(i[0], ':', i[1])
                raw_project['run']['env'][i[0]] = i[1]

            Path()['.chocolate'] = raw_project
            console.print('[green]All envs are added.')

    elif args.action == 'flags':
        project = ensure_project()
        raw_project = json.loads(~Path()['.chocolate'])
        raw_project['run']['flags'] = ' '.join(args.pkgs)
        Path()['.chocolate'] = raw_project
        console.print('[green]Flags updated.')
    elif args.action == 'run-quite':
        project = ensure_project()
        env = project['run', 'env']
        flags = project['run', 'flags']
        venv = prj.VenvManager('.venv')
        start = time.time()
        venv.run(project['run', 'startfile'], flags, env)
    else:
        console.print('[on red]Wrong commands.')


if __name__ == "__main__":
    main()
