# Chocolate Project Manager

Chocolate Project Manager (`pychocolate`) is a command-line tool for managing projects with virtual environments, dependencies, and environment variables.

## Features
- Create new projects
- Run projects with virtual environments
- Add and reinstall dependencies
- Manage environment variables and runtime flags

## Installation
Install `pychocolate` via pip:

```sh
pip install gochocolatego
```

## Usage
Run the `chocolate` command with different options to manage your projects.

### Create a New Project
```sh
chocolate new -n project_name -m main_file.py
```

### Run the Project
```sh
chocolate run
```

### Add Dependencies
```sh
chocolate add package_name
```

### Reinstall Dependencies
```sh
chocolate reinstall
```

### Manage Environment Variables
- Get environment variables:
  ```sh
  chocolate env get
  ```
- Remove environment variables:
  ```sh
  chocolate env rem ENV_KEY
  ```
- Add environment variables:
  ```sh
  chocolate env VAR_NAME=value
  ```

### Set Runtime Flags
```sh
chocolate flags --flag1 --flag2
```

## License
This project is licensed under the MIT License.

## Author
Chocolateisfr
