import os
import argparse
import sys
from paramiko import sftp
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from log import setup_logging, custom_print_format
from path import Path
from config import create_zip
from help import ensure_help, short_help
import project_manager as prj
from project_manager import CONFIG
from sftp import Sftp
from template import executer, hashfind

console = Console()
path = Path()
log = setup_logging(print_callback=custom_print_format)


def convert_dict_to_table(data):
    """
    Convert a dictionary to a Rich table.

    Args:
        data (dict): The dictionary to convert.

    Returns:
        Table: A Rich Table object representing the dictionary.
    """
    table = Table(show_header=False)
    for key, value in data.items():
        table.add_row(str(key), str(value))
    return table


def ensure_env_variables():
    """
    Ensure that all required environment variables are set.

    Prompts the user for input if any variables are missing from the project configuration.
    """
    log.info("Starting to ensure environment variables.")
    project = get_project_config()
    for key in project["startupEnv"]:
        if key not in project.config["environmentVariables"]:
            log.info("Requesting input for missing environment variable: %s", key)
            result = input().strip()
            project.config["environmentVariables"][key] = result
    project.commit()
    log.info("Environment variables have been ensured.")


def get_project_config():
    """
    Fetch the current project configuration.

    Returns:
        dict: The project configuration.

    Raises:
        SystemExit: If no project is found.
    """
    log.info("Fetching project configuration.")
    project = prj.get_config()
    if not project:
        log.critical("No project found. Please create a project first.")
        quit(1)
    log.info("Project configuration fetched successfully.")
    return project


def handle_new_project(args):
    """
    Handle the creation of a new project.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    log.info("Attempting to create a new project.")
    if prj.get_config():
        log.critical("Project already exists.")
        log.critical(
            "You can't create a new project because .chocolate already exists."
        )
        quit(1)
    if len(args.pkgs) != 2:
        log.critical("Missing required arguments: 'main' or 'name'.")
        quit(1)

    log.info(
        "Creating a new project with name: %s and main file: %s.",
        args.pkgs[0],
        args.pkgs[1],
    )
    prj.setup_project(args.pkgs[0], args.pkgs[1])
    log.info("New project established successfully.")
    log.info("Project created successfully. Use `chocolate run` to start.")


def run(args):
    """
    Execute the main run process of the project.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    log.info("Starting the run process.")
    ensure_env_variables()
    project = get_project_config()
    log.info("Running the startfile.")
    if args.reinstall:
        log.info("Reinstall flag detected, proceeding with reinstallation.")
        handle_reinstall()
    env = project["environmentVariables"]
    flags = project["flagsString"]
    venv = prj.VenvManager()
    try:
        log.info("Running the project startfile: %s.", project["mainFile"])
        console.print(Markdown("---"))
        venv.run(project["mainFile"], flags, env)
        console.print(Markdown("---"))
        log.info("Process finished.")

    except Exception as e:
        log.critical("Project execution failed. Error: %s", e)


def handle_package_installation(packages):
    """
    Handle the installation of packages.

    Args:
        packages (list): List of packages to install.
    """
    log.info("Starting the package installation process for packages: %s.", packages)
    project = get_project_config()
    venv = prj.VenvManager()
    res = Panel("", title="Output")
    with Live(res, refresh_per_second=4) as live:
        val = ""
        for pkg in packages:
            try:
                for i in venv.install(pkg):
                    val += i + "\n"
                    res.renderable = val
            except Exception as err:
                log.error("Problem while installing package %s: %s", pkg, err)
            else:
                log.info("Package %s installed successfully.", pkg)
            if pkg not in project.config["requirements"]:
                log.info("New package added: %s.", pkg)
                project.config["requirements"].append(pkg)

    path[CONFIG] = project.config
    log.info("All packages installed successfully.")


def handle_env_action(args):
    """
    Handle actions related to environment variables.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    log.info("Handling environment action: %s.", args.pkgs[0])
    try:
        project = get_project_config()
        raw_project = project.config
        if args.pkgs[0] == "list":
            log.info("Listing all environment variables.")
            log.info(convert_dict_to_table(project["environmentVariables"]))
        elif args.pkgs[0] == "remove":
            log.info("Removing environment keys.")
            for key in args.pkgs[1:]:
                log.info("Removing key from environment: %s.", key)
                raw_project["environmentVariables"].pop(key, None)
            path[CONFIG] = raw_project
        elif args.pkgs[0] == "private":
            for key in args.pkgs[1:]:
                if key in raw_project["privateEnv"]:
                    log.info("Making key public: %s.", key)
                    raw_project["private_env"].remove(key)
                else:
                    log.info("Making key private: %s.", key)
                    raw_project["privateEnv"].append(key)
            path[CONFIG] = raw_project
        else:
            log.info("Adding environment variables.")
            for env_var in args.pkgs:
                key, value = env_var.split("=", 1)
                if key in ["list", "remove"]:
                    log.critical("Invalid environment key name: %s.", key)
                    quit(1)
                raw_project["environmentVariables"][key] = value
                log.info("Added/edited environment variable: %s.", key)
            path[CONFIG] = raw_project
        log.info("All environment actions have been completed.")
    except Exception as e:
        log.critical("Error handling environment action: %s", e)


def handle_flags(args):
    """
    Handle updates to project flags.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    log.info("Handling flags update with values: %s.", args.pkgs)
    try:
        raw_project = get_project_config().config
        raw_project["flagsString"] = " ".join(args.pkgs)
        log.info("Flags have been updated.")
        path[CONFIG] = raw_project
    except Exception as e:
        log.critical("Error handling flags update: %s", e)


def custom_action(args):
    """
    Handle custom actions defined in the project.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    log.info("Processing custom action: %s.", args.pkgs[0])
    try:
        project = get_project_config()
        if args.pkgs[0] == "add":
            log.info("Adding a custom action.")
            if args.input:
                args.pkgs.append(open(args.input).read())
            project.config["actionsScript"][args.pkgs[1]] = args.pkgs[2]
            path[CONFIG] = project.config
        elif args.pkgs[0] == "remove":
            log.info("Removing a custom action.")
            project.config["actionsScript"].pop(args.pkgs[1])
            path[CONFIG] = project.config
        else:
            log.info("Executing custom actions: %s.", args.pkgs)
            for i in args.pkgs:
                i = project["actionsScript"][i].split("\n")
                for j in i:
                    os.system(j)
    except Exception as e:
        log.critical("Error executing custom action: %s", e)


def handle_path(args):
    """
    Handle actions related to project paths.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    try:
        log.info("Handling path action: %s.", args.pkgs[0])
        project = get_project_config()
        if args.pkgs[0] == "exclude":
            for path in args.pkgs[1:]:
                log.info("Excluding path: %s.", path)
                if path not in project["exclude"]:
                    project["exclude"].append(path)
            project.commit()
        elif args.pkgs[0] == "include":
            for path in args.pkgs[1:]:
                log.info("Including path: %s.", path)
                project["exclude"].remove(path)
            project.commit()
        elif args.pkgs[0] == "list":
            print("Excludes:")
            print(", ".join(project["exclude"]))
    except Exception as e:
        log.critical("Error handling path action: %s", e)


def handle_ask(args):
    """for for_ask in project["startupEnv"]:
        if for_ask not in env:
            print(f"[green]Enter the {for_ask} value: ")
            res = input()
            project["environmentVariables", for_ask] = res
        project.commit()

    Manage the list of environment variables to ask for.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    vars = args.pkgs
    project = get_project_config()
    for i in vars:
        if i in project["startupEnv"]:
            project["startupEnv"].remove(i)
            log.info("%s removed from ask_for list.", i)
        else:
            project["startupEnv"].append(i)
            log.info("%s added to ask_for list.", i)
    project.commit()


def handle_remove(args):
    """
    Remove the project configuration file.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    os.remove(CONFIG)


def handle_config(args):
    """
    Display the current project configuration.

    Args:
        args (argparse.Namespace): The command line arguments.
    """
    console.print(Pretty(get_project_config().config))


def handle_version(args):
    console.print("[blue]Chocolate [/blue](4.0.2-beta)")


def export(args):
    """
    Export the project to a specified location or a default location.

    Args:
        args (argparse.Namespace): The command line arguments.y
    """
    log.info(
        "Exporting project to %s.", args.output if args.output else "default location"
    )
    try:
        project = get_project_config()
        name = args.output if args.output else project["info"]["name"] + ".zip"
        make_executer()
        create_zip(name, ".", project["exclude"])
        log.info("Export completed successfully.")
    except Exception as e:
        log.critical("Error during export: %s", e)


def handle_reinstall(*_):
    project = get_project_config()
    handle_package_installation(project["requirements"])


def handle_sandbox(args):
    """Running scripts in sandbox mode"""
    log.info("Starting the run process as sandbox mode.")
    ensure_env_variables()
    project = get_project_config()
    log.info("Running the startfile.")
    if args.reinstall:
        log.info("Reinstall flag detected, proceeding with reinstallation.")
        handle_reinstall()
    env = project["environmentVariables"]
    flags = project["flagsString"]
    venv = prj.VenvManager()
    if len(args.pkgs) != 3:
        log.critical(
            "Usage `chocolate sandbox <memory limit in MB> <cpu time in seconds> <cpu freq in MH>`, Use -1 as unlimited."
        )
        quit(1)
    try:
        log.info("Running the project startfile: %s.", project["mainFile"])
        console.print(Markdown("---"))
        venv.run_sandbox(
            project["mainFile"], flags, env, args.pkgs[0], args.pkgs[1], args.pkgs[2]
        )
        console.print(Markdown("---"))
        log.info("Process finished.")

    except Exception as e:
        log.critical("Project execution failed. Error: %s", e)

def handle_ssh(args):
    project = get_project_config()
    vals = args.pkgs
    if len(vals) != 4:
        log.critical('Wrong usage. use chocolate ssh --help')
    
    project['sshHost'] = vals[0]
    project['sshPort'] = int(vals[1])
    project['sshUsername'] = vals[2]
    project['sshPassword'] = vals[3]
    log.info('Done.')


def handle_sync(args):
    project = get_project_config()
    if (
        not (ip := project["sshHost"])
        or not (username := project["sshUsername"])
        or not (password := project["sshPassword"])
        or not (port := project["sshPort"])
    ):
        log.critical("SSH server details are incomplete.")
        quit(1)
    make_executer()
    client = Sftp(ip, username, password, port)
    client.sync(project["info", "name"], project['exclude'])
    log.info("Running...")

    res = Panel("", title="Ssh Output")
    with Live(res, refresh_per_second=4) as live:
        txt = ""
        for i in client.run(project["info"]["name"]):
            txt += i + "\n"
            res.renderable = txt


def make_executer():
    project = get_project_config()
    deps = "\n".join(project["requirements"])
    env = "\n".join([f"{i}={j}" for i, j in project["environmentVariables"].items()])
    flags = project["flagsString"]
    with open(".env", "+w") as fp:
        fp.write(env)
    with open(".flags", "+w") as fp:
        fp.write(flags)
    with open("requirements.txt", "+w") as fp:
        fp.write(deps)
    with open("run.sh", "+w") as fp:
        fp.write(executer.format(project["mainFile"]))
    with open("hash.sh", "+w") as fp:
        fp.write(hashfind)
    log.info("chocolate-free project is ready.")


def handle_cmd(args):
    project = get_project_config()
    if (
        not (ip := project["sshHost"])
        or not (username := project["sshUsername"])
        or not (password := project["sshPassword"])
        or not (port := project["sshPort"])
    ):
        log.critical("SSH server details are incomplete.")
        quit(1)
    
    client = Sftp(ip, username, password, port)
    
    res = Panel("", title="Ssh Output")
    with Live(res, refresh_per_second=4) as live:
        txt = ""
        for i in client.exec(' '.join(sys.argv[2:])):
            txt += i + "\n"
            res.renderable = txt

def main():
    """
    Main entry point for the Chocolate Project Manager.

    Parses command line arguments and executes the specified action.
    """

    parser = argparse.ArgumentParser(
        description="Chocolate Project Manager.", add_help=False
    )
    parser.add_argument("action", type=str, help="Action")
    parser.add_argument("-o", "--output", type=str, help="Output file path.")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-r", "--reinstall", action="store_true")
    parser.add_argument("-i", "--input", required=False)
    parser.add_argument(
        "pkgs", nargs="*", help="Raw input after 'add' action", default=[]
    )

    args = parser.parse_args()

    actions = {
        "new": handle_new_project,
        "add": lambda args: handle_package_installation(args.pkgs),
        "reinstall": handle_reinstall,
        "env": handle_env_action,
        "flags": handle_flags,
        "run": run,
        "export": export,
        "action": custom_action,
        "path": handle_path,
        "ask_for": handle_ask,
        "remove": handle_remove,
        "config": handle_config,
        "version": handle_version,
        "sandbox": handle_sandbox,
        "sync": handle_sync,
        "ssh": handle_ssh,
        "cmd": handle_cmd,
        "help": lambda x: console.print(convert_dict_to_table(short_help)),
    }

    if args.action in actions or args.action == "help":
        ensure_help(args)
        actions[args.action](args)
    else:
        log.error("Unknown action requested.")


if __name__ == "__main__":
    main()
