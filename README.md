# jacoco-filter

A command-line tool to filter [JaCoCo](https://www.jacoco.org/jacoco/) XML code coverage reports based on file, class, and method rules — and to update coverage counters accordingly.


- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration and Usage](#configuration-and-usage)
  - [CLI Options](#cli-options)
  - [Configuration File: `jacoco_filter.toml`](#configuration-file-jacoco_filtertoml)
- [Rule Syntax and Examples](#rule-syntax-and-examples)
  - [Supported Scopes](#supported-scopes)
  - [Wildcards](#wildcards)
  - [Rule Examples](#rule-examples)
    - [File] Rules](#file-rules)
    - [Class Rules](#class-rules)
    - [Method Rules](#method-rules)
- [Output Behavior](#output-behavior)

---

## Requirements

- Python 3.12+
- `lxml` (for XML parsing)
- `pytest` (for testing and development)

---

## Quick Start

### Command Line Usage

Run the tool directly with CLI arguments:

```bash
python3 main.py --inputs "**/jacoco.xml" --rules rules.txt
```

### Github Actions Usage

Run the tool in a GitHub Actions workflow:

```yaml
jobs:
  filter:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - uses: actions/setup-python@v5.1.1
        with:
          python-version: '3.12'

      - name: Run jacoco-filter
        uses: MoranaApps/jacoco-filter@v1.0.0
        with:
          config: jacoco_filter.toml
          verbose: true
```

### Sample `rules.txt`

```text
file:*Spec.scala
class:com.example.internal.*
method:get*
```
> Update the `rules.txt` file with your specific filtering rules. Each line should follow the format `<scope>:<pattern>`.

This filters all matching JaCoCo XML files using the provided rules.

---

## Configuration and Usage

You can use either:

- **Command-line arguments** (for ad-hoc usage or CI integration)
- **Configuration file** (`jacoco_filter.toml` for persistent setups)

> Note:
> - Either `--inputs` or `[inputs]` in config must be provided.
> - Either `--rules` or `rules` must be provided.

### CLI Options

| Argument           | Type           | Description                                                                 | Required | Example                                                   |
|--------------------|----------------|-----------------------------------------------------------------------------|:--------:|-----------------------------------------------------------|
| `--inputs`         | list of globs  | Glob patterns to locate JaCoCo XML input files.                            |   Yes*   | `"**/jacoco.xml"`, `"modules/*/coverage-*.xml"`           |
| `--exclude-paths`  | list of globs  | Patterns to exclude files or folders. Case-sensitive, uses `fnmatchcase()`. |    No    | `"**/test/**"`, `"*/legacy/**"`                           |
| `--rules`          | file path      | Path to file containing filtering rules.                                    |   Yes*   | `"rules.txt"`                                             |
| `--config`         | toml file      | Optional configuration file (defaults to `jacoco_filter.toml`).             |    No    | `"jacoco_filter.toml"`                                    |

>- Glob patterns must include filenames (`**/jacoco.xml`) — directories alone will not match.
>- You can specify multiple values for both `--inputs` and `--exclude-paths`.

---

### Configuration File: `jacoco_filter.toml`

Use this file to define inputs, exclusion rules, and filtering rules.

#### Example

```toml
inputs = [
  "examples/project/**/sample.xml",
  "example/module*/**/*.xml"
]

exclude_paths = [
  "**/module_A/**"
]

rules = [
  "file:*Spec.scala",
  "file:HelperUtil.scala",
  "class:com.example.MyClass",
  "method:get*",
  "method:TestSpec#test*"
]
```

> **Important:** Command-line arguments always override values from the configuration file.

## Rule Syntax and Examples

Each rule has the following format:

```
<scope>:<pattern>
```

### Supported Scopes

| Scope    | Description                                                  |
|----------|--------------------------------------------------------------|
| `file`   | Source file name (e.g. `*Test.scala`, `Helper*.java`)        |
| `class`  | Fully-qualified class name (e.g. `com.example.MyClass`)      |
| `method` | Method name or `Class#method` format                         |

Rules are matched using `fnmatchcase()` (shell-style, case-sensitive).

### Wildcards

| Symbol   | Meaning                            |
|----------|------------------------------------|
| `*`      | Matches any sequence of characters |
| `?`      | Matches any single character       |
| `[abc]`  | Matches one character from the set |

---

### Rule Examples

#### File Rules

```
file:*.scala
file:*Test*
file:SpecHelper.scala
```

#### Class Rules

```
class:com.example.*
class:*.TestClass
class:com.*.util.*Helper
class:MainApp
```

#### Method Rules

```
method:get*
method:UserController#get*
method:com.example.*Service#handle*
method:Foo#toString
```

---

## Output Behavior

For each input file matched, a filtered XML file is generated in the same directory.

### Example

If this file is processed:

```
modules/core/target/site/jacoco.xml
```

Then this output is created:

```
modules/core/target/site/jacoco.filtered.xml
```
