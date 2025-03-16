from ast import arg
import os
import time
import argparse
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

try:
    from log import setup_logging, info, error
    from path import Path
    from config import ensure_length, create_zip
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
    log.info("Starting to ensure environment variables.")
    project = get_project_config()
    for key in project['ask_for']:
        if key not in project.config['run']['env']:
            log.info(f"Requesting input for missing environment variable: {key}")
            result = input().strip()
            project.config['run']['env'][key] = result
    path['.chocolate'] = project.config
    log.info("Environment variables have been ensured.")


def get_project_config():
    log.info("Fetching project configuration.")
    project = prj.get_config()
    if not project:
        log.critical("No project found. Please create a project first.")
        quit(1)
    log.info("Project configuration fetched successfully.")
    return project


def handle_new_project(args):
    log.info("Attempting to create a new project.")
    if prj.get_config():
        log.critical("Project already exists.")
        log.critical("You can't create a new project because .chocolate already exists.")
        quit(1)
    if not args.main or not args.name:
        log.critical("Missing required arguments: 'main' or 'name'.")
        quit(1)

    log.info(f"Creating a new project with name: {args.name} and main file: {args.main}.")
    prj.establish_project(args.name, args.main, '')
    log.info("New project established successfully.")
    log.info("Project created successfully. Use `chocolate run` to start.")


def run(args):
    log.info("Starting the run process.")
    ensure_env_variables()
    project = get_project_config()
    log.info("Running the startfile.")
    if args.reinstall:
        log.info("Reinstall flag detected, proceeding with reinstallation.")
        handle_reinstall()
    env = project['run', 'env']
    flags = project['run', 'flags']
    venv = prj.VenvManager('.venv')
    try:
        log.info(f"Running the project startfile: {project['run', 'startfile']}.")
        console.print(Markdown('---'))
        out = venv.run(project['run', 'startfile'], flags, env)
        console.print(Markdown('---'))
        log.info(f"Proccess finished.")
        
    except Exception as e:
        log.critical(f"Project execution failed. Error: {e}")


def handle_package_installation(packages):
    log.info(f"Starting the package installation process for packages: {packages}.")
    project = get_project_config()
    venv = prj.VenvManager('.venv')

    with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
        task = progress.add_task("Processing...", total=len(packages))
        for pkg in packages:
            try:
                log.info(f"Installing package: {pkg}.")
                venv.install(pkg)
            except Exception as err:
                log.error(f"Problem while installing package {pkg}: {err}")
            else:
                log.info(f"Package {pkg} installed successfully.")
            progress.advance(task)
            if pkg not in project.config['requirements']:
                log.info(f"New package added: {pkg}.")
                project.config['requirements'].append(pkg)

    path['.chocolate'] = project.config
    log.info("All packages installed successfully.")


def handle_reinstall(args=None):
    log.info("Starting reinstallation process.")
    try:
        raw_project = get_project_config().config
        venv = prj.VenvManager('.venv')

        with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as progress:
            task = progress.add_task("Processing...", total=len(raw_project['requirements']))
            for pkg in raw_project['requirements']:
                log.info(f"Reinstalling package: {pkg}.")
                venv.install(pkg)
                progress.advance(task)

        log.info("Reinstallation process completed successfully.")
    except Exception as e:
        log.critical(f"Reinstallation failed. Error: {e}")


def handle_env_action(args):
    log.info(f"Handling environment action: {args.pkgs[0]}.")
    try:
        project = get_project_config()
        raw_project = project.config
        if args.pkgs[0] == 'list':
            log.info("Listing all environment variables.")
            log.info(convert_dict_to_table(project['run', 'env']))
        elif args.pkgs[0] == 'remove':
            log.info("Removing environment keys.")
            for key in args.pkgs[1:]:
                log.info(f"Removing key from environment: {key}.")
                raw_project['run']['env'].pop(key, None)
            path['.chocolate'] = raw_project
        elif args.pkgs[0] == 'private':
            for key in args.pkgs[1:]:
                if key in raw_project['private_env']:
                    log.info(f"Making key private: {key}.")
                    raw_project['private_env'].remove(key)
                else:
                    log.info(f"Making key public: {key}.")
                    raw_project['private_env'].append(key)
            path['.chocolate'] = raw_project
        else:
            log.info("Adding environment variables.")
            for env_var in args.pkgs:
                key, value = env_var.split('=', 1)
                if key in ['list', 'remove']:
                    log.critical(f"Invalid environment key name: {key}.")
                    quit(1)
                raw_project['run']['env'][key] = value
                log.info(f"Added/edited environment variable: {key}.")
            path['.chocolate'] = raw_project
        log.info("All environment actions have been completed.")
    except Exception as e:
        log.critical(f"Error handling environment action: {e}")


def handle_flags(args):
    log.info(f"Handling flags update with values: {args.pkgs}.")
    try:
        raw_project = get_project_config().config
        raw_project['run']['flags'] = ' '.join(args.pkgs)
        log.info("Flags have been updated.")
        path['.chocolate'] = raw_project
    except Exception as e:
        log.critical(f"Error handling flags update: {e}")


def custom_action(args):
    log.info(f"Processing custom action: {args.pkgs[0]}.")
    try:
        project = get_project_config()
        if args.pkgs[0] == 'add':
            log.info("Adding a custom action.")
            if args.input:
                args.pkgs.append(open(args.input).read())
            project.config['actions'][args.pkgs[1]] = args.pkgs[2]
            path['.chocolate'] = project.config
        elif args.pkgs[0] == 'remove':
            log.info("Removing a custom action.")
            project.config['actions'].pop(args.pkgs[1])
            path['.chocolate'] = project.config
        else:
            log.info(f"Executing custom actions: {args.pkgs}.")
            for i in args.pkgs:
                i = project['actions'][i].split('\n')
                for j in i:
                    os.system(j)
    except Exception as e:
        log.critical(f"Error executing custom action: {e}")




def handle_path(args):
    try:
        log.info(f"Handling path action: {args.pkgs[0]}.")
        project = get_project_config()
        if args.pkgs[0] == 'exclude':
            for path in args.pkgs[1:]:
                log.info(f"Excluding path: {path}.")
                if path not in project['exclude']:
                    project['exclude'].append(path)
            project.commit()
        elif args.pkgs[0] == 'include':
            for path in args.pkgs[1:]:
                log.info(f"including path: {path}.")
                project['exclude'].remove(path)
            project.commit()
        elif args.pkgs[0] == 'list':
            print('Excludes:')
            print(', '.join(project['exclude']))
    except Exception as e:
        log.critical(f"Error handling path action: {e}")


def export(args):
    log.info(f"Exporting project to {args.output if args.output else 'default location'}.")
    try:
        project = get_project_config()
        name = args.output if args.output else project['name']+'.zip'
        create_zip(name, '.', project['exclude'])
        log.info("Export completed successfully.")
    except Exception as e:
        log.critical(f"Error during export: {e}")


def main():
    log.info("Starting Chocolate Project Manager.")
    parser = argparse.ArgumentParser(description="Chocolate Project Manager.", add_help=False)
    parser.add_argument("action", type=str, help="Action")
    parser.add_argument('-n', '--name', help='Name of the project.')
    parser.add_argument("-m", "--main", type=str, help="Main file name.")
    parser.add_argument('-o', '--output', type=str, help="Output file path.")
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-r', '--reinstall', action='store_true')
    parser.add_argument('-i', '--input', required=False)
    parser.add_argument("pkgs", nargs="*", help="Raw input after 'add' action", default=[])

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
        log.error("Unknown action requested.")


if __name__ == "__main__":
    main()
