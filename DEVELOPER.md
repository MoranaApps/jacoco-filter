# Jacoco Report GitHub Action - Developer Guide

- [Project Setup](#project-setup)
- [Run Locally](#run-locally)
- [Run Pylint Check Locally](#run-pylint-check-locally)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Run Unit Test](#run-unit-test)
- [Code Coverage](#code-coverage)


## Project Setup

If you need to build the action locally, follow these steps for project setup:

### Prepare the Environment

```shell
python3 --version
```

### Set Up Python Environment

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run Locally

Once your environment is ready, you can run `jacoco-filter` directly using either the **command-line arguments** or the **TOML configuration file**.

### Run with CLI Arguments
```bash
python3 run_filter.py \
  --inputs "examples/project/**/sample.xml" "example/module*/**/*.xml" \
  --exclude-paths "**/module_A/**" \
  --rules examples/rules.txt
```

### Run with TOML Config

To run using the local `*-jacoco_filter.toml` config file:

```bash
python3 run_filter.py --config path/to/custom_jacoco_config.toml
```

> **Note:** You can still override values from the config file using CLI options like `--inputs`, `----exclude-paths` or `--rules`.

---

## Run Pylint Check Locally

This project uses [Pylint](https://pypi.org/project/pylint/) tool for static code analysis.
Pylint analyses your code without actually running it.
It checks for errors, enforces, coding standards, looks for code smells etc.
We do exclude the `tests/` file from the pylint check.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0.
We are aiming to keep our code quality high above the score 9.5.

Follow these steps to run Pylint check locally:

### Run Pylint

Run Pylint on all files that are currently tracked by Git in the project.

```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:

```shell
pylint jacoco_filter/run_filter.py
```

### Expected Output

This is the console expected output example after running the tool:

```shell
************* Module main
main.py:30:0: C0116: Missing function or method docstring (missing-function-docstring)

------------------------------------------------------------------
Your code has been rated at 9.41/10 (previous run: 8.82/10, +0.59)
```

---

## Run Black Tool Locally

This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project we are accepting the line length of 120 characters.
We also do exclude the `tests/` file from the black formatting.

Follow these steps to format your code with Black locally:

### Run Black

Run Black on all files that are currently tracked by Git in the project.

```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:

```shell
black jacoco_filter/run_filter.py
```

### Expected Output

This is the console expected output example after running the tool:

```shell
All done! ✨ 🍰 ✨
1 file reformatted.
```

---

## Run mypy Tool Locally

This project uses the [my[py]](https://mypy.readthedocs.io/en/stable/) tool, a static type checker for Python.

> Type checkers help ensure that you correctly use variables and functions in your code.
> With mypy, add type hints (PEP 484) to your Python programs,
> and mypy will warn you when you use those types incorrectly.
my[py] configuration is in `pyproject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy jacoco_filter/run_filter.py
``` 

---

## Run Unit Test

Unit tests are written using the Pytest framework. To run all the tests, use the following command:

```shell
pytest tests/
```

You can modify the directory to control the level of detail or granularity as per your needs.

To run a specific test, write the command following the pattern below:

```shell
pytest tests/run_filter.py::test_make_issue_key
```

---

## Code Coverage

This project uses [pytest-cov](https://pypi.org/project/pytest-cov/) plugin to generate test coverage reports.
The objective of the project is to achieve a minimal score of 80 %. We do exclude the `tests/` file from the coverage
report.

To generate the coverage report, run the following command:

```shell
pytest --cov=. tests/ --cov-fail-under=80 --cov-report=html -vv
```

See the coverage report on the path:

```shell
open htmlcov/index.html
```
