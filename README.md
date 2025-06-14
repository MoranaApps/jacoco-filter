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

Each rule must be on a separate line and follow the format:

```text
<scope>:<pattern>
```

Examples:

```text
class:com.example.MyClass
method:doSomething*
```

## Requirements

- Python 3.12+
- lxml (for XML parsing)
- pytest (for testing)