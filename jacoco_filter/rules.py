# jacoco_filter/rules.py

from dataclasses import dataclass
from pathlib import Path
from fnmatch import fnmatchcase


@dataclass
class FilterRule:
    scope: str  # "class" or "method"
    pattern: str

    def matches(self, target: str) -> bool:
        return fnmatchcase(target, self.pattern)


def load_filter_rules(path: Path) -> list[FilterRule]:
    rules = []

    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                raise ValueError(f"Invalid rule format on line {lineno}: '{line}'")

            scope, pattern = line.split(":", 1)
            scope = scope.strip().lower()
            pattern = pattern.strip()

            if scope not in {"class", "method"}:
                raise ValueError(f"Unsupported rule scope on line {lineno}: '{scope}'")

            if not pattern:
                raise ValueError(f"Empty pattern on line {lineno}")

            rules.append(FilterRule(scope=scope, pattern=pattern))

    return rules
