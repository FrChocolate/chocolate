import os
import time
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


try:
    from log import setup_logging
    from path import Path
    from config import ensure_length, create_zip_from_lists
    from help import ensure_help
    import project_manager as prj
except ImportError:
    quit(1)

console = Console()
path = Path()
log = setup_logging()


def convert_dict_to_table(data):
    table = Table(show_header=False)
    for key, value in data.items():
        table.add_row(str(key), str(value))
    return table


def ensure_env_variables():
    project = get_project_config()
    for key in project['ask_for']:
        if key not in project.config['run']['env']:
            console.print(f'[green]--> [blue]{key}: ', end='')
            result = input().strip()
            project.config['run']['env'][key] = result
    path['.chocolate'] = project.config


def get_project_config():
    project = prj.get_config()
    if not project:
        console.print(
            '[black on red]No project found. Please create a project first.[/]')
        quit(1)
    return project


def handle_new_project(args):
    log.info('Trying to make a new project.')
    if prj.get_config():
        log.critical('Project already exists.')
        console.print(
            "[black on red]You can't create a new project, .chocolate already exists.")
        quit(1)
    if not args.main or not args.name:
        console.print('[black on red]Missing arguments.')
        quit(1)

    console.print('Creating a new project.')
    prj.establish_project(args.name, args.main, '')
    log.info('New project established.')
    console.print('Project created successfully. Use `chocolate run`.')


def run(args):
    ensure_env_variables()
    project = get_project_config()
    log.info('Running the startfile.')
    if args.reinstall:
        handle_reinstall()
    env = project['run', 'env']
    flags = project['run', 'flags']
    venv = prj.VenvManager('.venv')
    try:
        venv.run(project['run', 'startfile'], flags, env)
    except:
        log.critical('Project execution failed/dumped.')


def handle_package_installation(packages):
    project = get_project_config()
    log.info(f'Requested to install {packages} packages.')
    console.print('[yellow]Installing packages.')
    venv = prj.VenvManager('.venv')

    with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
        task = progress.add_task("Processing...", total=len(packages))
        for pkg in packages:
            try:
                venv.install(pkg)
            except Exception as err:
                console.print(f'[red]{err}')
                log.error(f'Problem while installing {pkg}: {err}')
            else:
                log.info(f'Installed package {pkg} successfully.')
            progress.advance(task)
            if pkg not in project.config['requirements']:
                log.info(f'New package added {pkg}')
                project.config['requirements'].append(pkg)

    path['.chocolate'] = project.config
    console.print('[green]Installed all packages successfully.')


def handle_reinstall(args=None):
    raw_project = get_project_config().config
    console.print('[yellow]Reinstalling all packages.')
    log.info('Requesting a reinstall.')
    venv = prj.VenvManager('.venv')

    with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
        task = progress.add_task(
            "Processing...", total=len(raw_project['requirements']))
        for pkg in raw_project['requirements']:
            venv.install(pkg)
            progress.advance(task)

    console.print('[green]All packages installed successfully.')


def handle_env_action(args):
    project = get_project_config()
    raw_project = project.config
    if args.pkgs[0] == 'list':
        log.info('Listed all enviroment variables.')
        console.print(convert_dict_to_table(project['run', 'env']))
    elif args.pkgs[0] == 'remove':
        console.print('[green]Removing env keys')
        for key in args.pkgs[1:]:
            raw_project['run']['env'].pop(key, None)
            log.info(f'Removed {key} from the enviroment variables.')
            console.print(f'[red]Removed {key}.')
        path['.chocolate'] = raw_project
    elif args.pkgs[0] == 'private':
        for key in args.pkgs[1:]:
            if key in raw_project['private_env']:
                console.print(f'[yellow](warn) {key} is now public.')
                log.info(f'Made the key ({key}) public.')
                raw_project['private_env'].remove(key)
            else:
                console.print(f'[yellow](warn) {key} is now private.')
                log.info(f'Made the key ({key}) private.')
                raw_project['private_env'].append(key)
        path['.chocolate'] = raw_project
    else:
        console.print('[green]Adding env.')
        for env_var in args.pkgs:
            key, value = env_var.split('=', 1)
            if key in ['list', 'remove']:
                console.print(f'[red]You cannot name your env key {key}')
                quit(1)
            raw_project['run']['env'][key] = value
            log.info(f'Added/ Edited the key: {key}')

        path['.chocolate'] = raw_project
        console.print('[green]All envs are added.')


def handle_flags(args):
    raw_project = get_project_config().config
    raw_project['run']['flags'] = ' '.join(args.pkgs)
    log.info(f'Edited flags.')
    path['.chocolate'] = raw_project
    console.print('[green]Flags updated.')


def custom_action(args):
    project = get_project_config()
    if args.pkgs[0] == 'add':
        log.info('Adding a custom action.')
        if args.input:
            args.pkgs.append(open(args.input).read())
        project.config['actions'][args.pkgs[1]] = args.pkgs[2]
        path['.chocolate'] = project.config
    elif args.pkgs[0] == 'remove':
        log.info('Removing a custom action.')
        project.config['actions'].pop(args.pkgs[1])
        path['.chocolate'] = project.config
    else:
        log.info(f'Running actions {args.pkgs}')
        for i in args.pkgs:
            i = project['actions'][i].split('\n')
            for j in i:
                os.system(j)


def normalize_path(path):
    """Normalize the path to a standard format using relative paths."""
    return path.rstrip('/')


def handle_path(args):
    project = get_project_config()

    if args.pkgs[0] == 'include':
        ensure_length(args.pkgs[1:], 1, 1000)
        log.info('Adding new paths to the project paths.')

        for i in args.pkgs[1:]:
            normalized_path = normalize_path(i)

            # Check if the path exists
            if not os.path.exists(normalized_path):
                console.print(
                    f'[red] The path {normalized_path} does not exist.')
                continue

            # If it's an included path
            if normalized_path in project['paths']['include']:
                console.print(
                    f'[red] {normalized_path} is already in the include paths.')
            # If it's a subdirectory of an included path
            elif any(os.path.commonpath([normalized_path, existing_path]) == existing_path for existing_path in project['paths']['include']):
                console.print(
                    f'[red] {normalized_path} cannot be added as it is inside an existing include path.')
            else:
                console.print(
                    f'[green] Added {normalized_path} to the include paths.')
                project['paths']['include'].append(normalized_path)

        project.commit()

    elif args.pkgs[0] == 'exclude':
        ensure_length(args.pkgs[1:], 1, 1000)
        log.info('Removing paths from the project paths.')

        for i in args.pkgs[1:]:
            normalized_path = normalize_path(i)

            # Check if the path exists
            if not os.path.exists(normalized_path):
                console.print(
                    f'[red] The path {normalized_path} does not exist.')
                continue

            # If it's in include paths
            if normalized_path in project['paths']['include']:
                console.print(
                    f'[green] Removed {normalized_path} from the include paths.')
                project['paths']['include'].remove(normalized_path)

                # If it's a directory, check for any excluded files
                if os.path.isdir(normalized_path):
                    for file in os.listdir(normalized_path):
                        file_path = os.path.join(normalized_path, file)
                        if file_path in project['paths']['exclude']:
                            console.print(
                                f'[yellow] {file_path} was in the exclude paths. It will be removed now.')
                            project['paths']['exclude'].remove(file_path)

            # If it's a file inside an included folder
            elif any(normalized_path == os.path.join(existing_path, file) for existing_path in project['paths']['include'] for file in os.listdir(existing_path)):
                console.print(
                    f'[green] Excluded {normalized_path} from the included path.')
                project['paths']['exclude'].append(normalized_path)
            # If it's in exclude paths
            elif normalized_path in project['paths']['exclude']:
                console.print(
                    f'[green] Removed {normalized_path} from the exclude paths.')
                project['paths']['exclude'].remove(normalized_path)

            else:
                console.print(
                    f'[red] {normalized_path} is not in the include or exclude paths.')

        project.commit()


def export(args):
    project = get_project_config()
    name = args.output if args.output else project['name']+'.zip'
    create_zip_from_lists(
        name, project['paths', 'include'], project['paths', 'exclude'])


def main():
    parser = argparse.ArgumentParser(
        description="Chocolate Project Manager.", add_help=False)
    parser.add_argument("action", type=str, help="Action")
    parser.add_argument('-n', '--name', help='Name of the project.')
    parser.add_argument("-m", "--main", type=str, help="Main file name.")
    parser.add_argument('-o', '--output', type=str, help="Output file path.")
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-r', '--reinstall', action='store_true')
    parser.add_argument('-i', '--input', required=False)
    parser.add_argument("pkgs", nargs="*",
                        help="Raw input after 'add' action", default=[])

    args = parser.parse_args()

    actions = {
        'new': handle_new_project,
        'add': lambda args: handle_package_installation(args.pkgs),
        'reinstall': handle_reinstall,
        'env': handle_env_action,
        'flags': handle_flags,
        'run': run,
        'export': export,
        "action": custom_action,
        "path": handle_path
    }

    if args.action in actions or args.action == 'help':
        ensure_help(args)
        actions[args.action](args)
    else:
        console.print("[red]Unknown action.")


if __name__ == "__main__":
    main()
