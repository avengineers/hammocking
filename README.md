# hammock
Automatic mocking tool for C

## CI

[![Ubuntu](https://github.com/avengineers/hammock/actions/workflows/linux.yml/badge.svg)](https://github.com/avengineers/hammock/actions/workflows/linux.yml)

[![Windows](https://github.com/avengineers/hammock/actions/workflows/windows.yml/badge.svg)](https://github.com/avengineers/hammock/actions/workflows/windows.yml)

## Build

This project uses [Pipenv](https://pypi.org/project/pipenv/). Run the following command to install it using your system's Python >=3.6 installation:
```shell
pip install pipenv
```

To create a virtual environment for development run:
```shell
pipenv install --dev
```

To debug your Python code in VS Code you need to activate the virtual environment. To activate this project's virtualenv, run:
```shell
pipenv shell
```

Run a command, e.g. pytest, inside the virtualenv with
```shell
pipenv run pytest -v
```

TODO: Somehow pytest fails when already installed in the system's python distribution. Uninstall it:
```shell
pip uninstall pytest
```
