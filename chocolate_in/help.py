import subprocess
from rich import print
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

short_help = dict(
    run="Runs the app specified in .chocolate.run.main with various options for logging and testing.",
    env="Manages environment variables, including adding, removing, and setting privacy.",
    new="Creates a new project with a specified name and main file path.",
    reinstall="Reinstalls all dependencies for the project.",
    flags="Sets or clears flags for running the project with custom parameters.",
    export="Exports the project as a zip file with options to include/exclude certain files.",
    path="Includes or excludes specific paths in the project.",
    action="Handles custom actions for the project, allowing addition, removal, and execution.",
    sandbox="Runs the project in a controlled environment with resource limits.",
    ask_for="Manages environment variables that should be asked for during startup.",
    remove="Deletes the project configuration file (.chocolate).",
    config="Displays the current configuration of the project.",
    version="Shows the current version of the Chocolate Project Manager.",
)


def ensure_help(args):
    if args.help:
        subprocess.run(["choco-help", args.action])
        quit()
