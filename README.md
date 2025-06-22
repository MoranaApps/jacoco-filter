# jacoco-filter

A command-line tool to filter [JaCoCo](https://www.jacoco.org/jacoco/) XML coverage reports based on class and method patterns, and to adjust coverage counters accordingly.

- [Example usage](#-example-usage)
- [Controlling the Application](#-controlling-the-application)
- [Configuration File](#configuration-file)
- [Requirements](#requirements)
- [Rule Format](#rule-format)
  - [Supported Scopes](#supported-scopes)
  - [Wildcards](#wildcards)
  - [Valid Rule Examples](#valid-rule-examples)
    - [File](#file)
    - [Class](#class)
    - [Method](#method)

---

## 🧪 Example usage

```bash
python3 main.py --input examples/sample.xml --rules examples/rules.txt
```

## 🔧 Controlling the Application

`jacoco-filter` provides flexible CLI options and config file support to simplify working with large, modular projects. You must provide either `--inputs` via CLI or define them in the config file (`jacoco_filter.toml`).

| Argument         | Type          | Description                                                                           | Required | Example                                                |
|------------------|---------------|---------------------------------------------------------------------------------------|:--------:|--------------------------------------------------------|
| `--inputs`       | list of globs | Glob patterns or directories to recursively collect input XML files.                  |   Yes*   | `"target/**/jacoco.xml"`, `"modules/*/coverage-*.xml"` |
| `--exclude-paths` | list of globs | Glob patterns to ignore certain files or folders during discovery. Case-sensitive.    |    No    | `"**/test/**"`, `"*/legacy/**"`                        |
| `--rules`        | file path     | Text file with filtering rules for class/method/file exclusions.                      |   Yes*   | `"rules/exclude.txt"`                                  |
| `--config`       | toml file     | Optional path to config file (`jacoco_filter.toml` used by default)                   |    No    | `jacoco_filter.toml`                                  |

> * At least one of `--inputs` or `--config` must be provided. Similarly, either `--rules` or inline `rules` in the config must be present.

>- Globs are **explicit**: patterns must include filenames (e.g., `**/jacoco.xml`), not just directory paths.
>- Pattern matching uses `fnmatchcase()` — case-sensitive and shell-style (`*`, `?`, `[abc]`).
>- You can mix multiple globs and directories in `--inputs` and `--exclude-paths`.

---

### 📦 Output Handling

For every input file discovered:

- A `separate filtered XML` is written next to the original file.
- The output file is named by appending `.filtered.xml` to the input name.

#### Example

If the tool finds:

```text
modules/core/target/site/jacoco.xml
```

It generates:

```text
modules/core/target/site/jacoco.filtered.xml
```

## Configuration File

You can define input globs, exclusion rules, and inline filtering rules inside a `jacoco_filter.toml` config file placed in your project root.

### Example

```toml
inputs = [
  "examples/project/**/sample.xml",
  "example/module*/**/*.xml"
]

exclude_paths = [
  "**/module_A/**"
]

inline_rules = [
  "file:*Spec.scala",
  "file:HelperUtil.scala",
  "class:com.example.MyClass",
  "method:get*",
  "method:TestSpec#test*"
]
```

> CLI options always override values from the config file.

## Requirements

- Python 3.12+
- `lxml` (for XML parsing)
- `pytest` (for testing)

## Rule Format

Each rule defines a class, file, or method to be excluded from coverage. Rules can be defined in an external file (`--rules`) or inline via the `jacoco_filter.toml` config file.

Format:
```text
<scope>:<pattern>
```

### Supported scopes:

- `file` — source file name (e.g. `*Test.scala`, `Helper*.java`)
- `class` — fully-qualified class name (dot-separated, e.g. `com.example.MyClass`)
- `method` — method name only or scoped as Class#method (e.g. `get*`, `MyClass#handle*`)

### Wildcards:

- Supported via `fnmatchcase()` (shell-style)
- Available characters:
  - `*` — any sequence of characters
  - `?` — any single character
  - `[seq]` — any character in sequence
- Matching is **case-sensitive**

### Valid Rule Examples

#### File
```text
file:*.scala               # All Scala source files
file:*Test*                # Any file containing "Test" in the name
file:SpecHelper.scala      # Exact match
```

#### Class
```text
class:com.example.*        # All classes in the package and subpackages
class:*.TestClass          # Any class ending in TestClass
class:com.*.util.*Helper   # All Helper classes under any util package
class:MainApp              # Simple class match
```

#### Method
```text
method:get*                              # Any method starting with get
method:UserController#get*               # Scoped to a specific class
method:com.example.*Service#handle*      # Class and method patterns matched together using fully-qualified class name
method:Foo#toString                      # Specific method in class Foo
```
