# jacoco-filter

A command-line tool to filter [JaCoCo](https://www.jacoco.org/jacoco/) XML coverage reports based on class and method patterns, and to adjust coverage counters accordingly.

---

## 🧪 Example usage

```bash
python3 main.py --input examples/sample.xml --rules examples/rules.txt --output output.xml
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
