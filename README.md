# jacoco-filter

A command-line tool to filter [JaCoCo](https://www.jacoco.org/jacoco/) XML coverage reports based on class and method patterns, and to adjust coverage counters accordingly.

- [Example usage](#-example-usage)
- [Controlling the Application](#-controlling-the-application)
- [Requirements](#requirements)
- [Rule Format](#rule-format)
  - [Supported Scopes](#supported-scopes)
  - [Wildcards](#wildcards)
  - [Valid Rule Examples](#valid-rule-examples)
    - [File](#file)
    - [Class](#class)
    - [Method](#method)


TODOs
DONE - update README with inputs
DONE - add examples
- add logic to keep multiple globs - input & exclude
- add logic for search for jacoco using globs
- prepares data for testing
- manually test the tool

---

## 🧪 Example usage

```bash
python3 main.py --input examples/sample.xml --rules examples/rules.txt --output output.xml
```

## 🔧 Controlling the Application

`jacoco-filter` provides powerful CLI options to simplify working with large and modular projects. It allows you to specify multiple input globs and define exclusions.

| Argument         | Type           | Description                                                                        | Example                                                                                    |
|------------------|----------------|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `--inputs`       | list of globs  | Glob patterns or directories to recursively collect input XML files.               | `"target/**/jacoco.xml"`, `"modules/*/coverage-*.xml"`                                    |
| `--exclude-paths`| list of globs  | Glob patterns to ignore certain files or folders during discovery. Case-sensitive. | `"**/test/**"`, `"*/legacy/**"`                                                            |
| `--rules`        | file path      | Text file with filtering rules for class/method/file exclusions.                   | `"rules/exclude.txt"`                                                                     |
| `--output`       | filename       | New filename to use for filtered results, saved next to each input file.           | `"jacoco.filtered.xml"`                                                    |

>- Globs are **explicit**: patterns must include filenames (e.g., `**/jacoco.xml`), not just directory paths.
>- Pattern matching uses `fnmatchcase()` — case-sensitive and shell-style (`*`, `?`, `[abc]`).
>- You can mix multiple globs and directories in `--inputs` and `--exclude-paths`.

---

### 📦 Output Handling

Regardless of how many inputs are discovered:

- The tool writes a **separate filtered XML** file next to each input.
- The output file uses the same folder, with a new **filename defined by** `--output` (e.g. `jacoco.filtered.xml`).

---

#### Example

If the following input is found:

```text
modules/core/target/site/jacoco.xml
```

and you run:

```bash
jacoco-filter \
--inputs "modules/**/jacoco.xml" \
--rules rules.txt \
--output jacoco.filtered.xml
```

Then the output will be:

```text
modules/core/target/site/jacoco.filtered.xml
```

## Requirements

- Python 3.12+
- lxml (for XML parsing)
- pytest (for testing)

## Rule Format

Each rule defines a class, file, or method to be excluded from coverage. Rules are written in the format:

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
