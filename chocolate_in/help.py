from rich import print
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

helps = dict(
    run="""
## chocolate run
-> This function runs the app specified inside .chocolate.run.main.
- Use `-o <log_file_name>` to log the entire output of the script.
- Use `-r` to reinstall dependencies before running the project.
- Use `-s` to run the app with `screen`.
- Use `-t` to run tests before starting.
""",
    env="""
## chocolate env
-> This function is used for declaring, removing, or getting environment variables.
- Use `remove key1 key2` to remove specified keys.
- Use `list` to list all environment variables.
- Use `key1=value1 key2=value2 ...` to set values.
- Use `private key1 key2 ...` to toggle a key's privacy.

__Private keys won't be exported with the export command.__

**You can't name your environment variable 'list', 'remove', or 'private'.**
""",
    new="""
## chocolate new
-> This function is used to create a new project.
- Use `-n <project name>` to specify the project name.
- Use `-m <main file.py>` to specify the main file path.
""",
    reinstall="""
## chocolate reinstall
-> This function is used to reinstall all dependencies.
""",
    flags="""
## chocolate flags
-> This function is used to set flags for running .chocolate.run.startfile.
- Use `flags flag1 flag2 flag3 flag4 ...` to add or overwrite flags.
- Use `flags ""` to remove all flags.
""",
    export="""
## chocolate export
-> This function is used to export the project into a zip file.
- Use `-o <output file>` to specify the output file.
- Use `-a` to export the entire folder (see the attachment).
- Use `-w` to avoid exporting the .chocolate file (not recommended).

**Attachment:** By default, the export function only exports the files and folders that are in the path. Run `chocolate path -h` to get help with adding or removing paths from the project.
""",
    path="""
## chocolate path
-> This function is used to include or exclude a path from the project.
- Use `include <path>` to enclude a path inside a project.
- Use `exclude <path>` to exclude a path inside a project.

**example**
```bash
chocolate path include assets/
chocolate path exclude assets/db.db
```
""")


def get(help_name):
    print(Panel(Markdown(
        helps[help_name], code_theme='dracula', inline_code_theme='dracula'), box.SQUARE))


def ensure_help(args):
    if args.action == 'help':
        for i in helps:
            get(i)
        quit()
    if args.help:
        get(args.action)
        quit()
