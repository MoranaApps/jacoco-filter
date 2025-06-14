# jacoco-filter

A command-line tool to filter [JaCoCo](https://www.jacoco.org/jacoco/) XML coverage reports based on class and method patterns, and to adjust coverage counters accordingly.

---

## 🚀 Features (v1.0.0 - Pilot)

- CLI interface for passing input/output files and filter rules
- Parses `jacoco.xml` into memory
- Filters classes or methods based on rules
- Resets coverage counters appropriately
- Serializes the modified report back to XML
- Packaged as a single executable via PyInstaller

---

## 🧪 Example usage

```bash
python3 main.py --input examples/sample.xml --rules examples/rules.txt --output output.xml
```

## Rule Format

Each rule defines a class or method to be **excluded from coverage**.  
Rules are written in the format:

```text
<scope>:<pattern>
```

### Supported scopes:
- `class` — fully-qualified class name (e.g. `com/example/MyClass`)
- `method` — method name only (e.g. `get*`)

### Wildcards:
- `*` allowed only at the beginning or end of the pattern
- Example: `method:get*` filters out any method starting with `get`

### Example rules.txt:
```text
class:com/example/MyClass
method:get*
```

## Requirements

- Python 3.12+
- lxml (for XML parsing)
- pytest (for testing)