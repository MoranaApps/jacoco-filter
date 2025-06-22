# jacoco_filter/rules.py
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from fnmatch import fnmatchcase
from typing import Optional


class ScopeEnum(str, Enum):
    FILE = "file"
    CLASS = "class"
    METHOD = "method"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


@dataclass
class FilterRule:
    scope: ScopeEnum  # "file", "class", or "method"
    pattern: str
    target_class_pattern: Optional[str] = field(init=False, default=None)
    target_method_pattern: Optional[str] = field(init=False, default=None)

    def __post_init__(self):
        if self.scope == ScopeEnum.METHOD:
            if "#" in self.pattern:
                self.target_class_pattern, self.target_method_pattern = (
                    self.pattern.split("#", 1)
                )
            else:
                self.target_class_pattern = None
                self.target_method_pattern = self.pattern

    def matches(self, target: dict) -> bool:
        try:
            match self.scope:
                case ScopeEnum.FILE:
                    return fnmatchcase(target["sourcefilename"], self.pattern)

                case ScopeEnum.CLASS:
                    return fnmatchcase(
                        target["fully_qualified_classname"], self.pattern
                    )

                case ScopeEnum.METHOD:
                    method_name = target["method_name"]
                    fqcn = target.get("fully_qualified_classname", "")
                    simple_class = target.get(
                        "simple_class_name", fqcn.split(".")[-1] if fqcn else ""
                    )

                    print(
                        f"[DEBUG] METHOD: fqcn={fqcn}, simple_class={simple_class}, method={method_name}"
                    )
                    print(
                        f"[DEBUG] Rule: class_pattern={self.target_class_pattern}, method_pattern={self.target_method_pattern}"
                    )

                    if self.target_class_pattern:
                        class_match = fnmatchcase(
                            fqcn, self.target_class_pattern
                        ) or fnmatchcase(simple_class, self.target_class_pattern)

                        if not class_match:
                            print(
                                f"[DEBUG] Rule '{self.pattern}' did not match class '{fqcn}' or '{simple_class}'"
                            )
                            return False

                    matched = fnmatchcase(method_name, self.target_method_pattern)
                    print(
                        f"[DEBUG] Matching method '{method_name}' with rule '{self.pattern}' => {matched}"
                    )
                    return matched

                case _:
                    return False

        except KeyError as e:
            raise KeyError(
                f"Missing key '{e.args[0]}' in target dict for rule: {self.scope}:{self.pattern}"
            )

    @staticmethod
    def is_valid_line(line: str) -> bool:
        line = line.strip()
        return (
            bool(line)
            and not line.startswith("#")
            and ":" in line
            and any(scope in line for scope in ScopeEnum)
        )

    @classmethod
    def parse(cls, line: str) -> "FilterRule":
        if ":" not in line:
            raise ValueError(f"Missing ':' in rule: '{line}'")

        scope, pattern = line.split(":", 1)
        scope = scope.strip()
        pattern = pattern.strip()

        if scope not in ScopeEnum:
            raise ValueError(f"Invalid scope '{scope}' in rule: '{line}'")

        if not pattern:
            raise ValueError(f"Empty pattern in rule: '{line}'")

        return cls(scope, pattern)


def load_filter_rules(path: Path) -> list[FilterRule]:
    rules = []

    with path.open("r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            # tady tohle zda se spatne odstrani koment u get* - over, kde vsude se neodstrani?
            line = strip_comment(raw_line.strip())
            if not line:
                continue

            if ":" not in line:
                raise ValueError(f"Invalid rule format on line {lineno}: '{line}'")

            if line.count(":") > 1:
                raise ValueError(f"Multiple colons found on line {lineno}: '{line}'")

            scope, pattern = line.split(":", 1)
            scope = scope.strip().lower()
            pattern = pattern.strip()

            if not ScopeEnum.has_value(scope):
                raise ValueError(f"Unsupported rule scope '{scope}' on line {line}")

            if not pattern:
                raise ValueError(f"Empty pattern on line {lineno}")

            rules.append(FilterRule(scope=ScopeEnum(scope), pattern=pattern))

    return rules


def strip_comment(line: str) -> str:
    """
    Strips trailing comments from a rule line, preserving '#' used in method patterns.
    A '#' is considered a comment only if it is preceded by a space.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return ""

    # This regex matches the rule, preserving # inside patterns (e.g. MyClass#get*)
    # and removes the comment if there's a space before the # (e.g. '  # comment')
    comment_match = re.search(r"(.*?)\s+#.*$", line)
    if comment_match:
        return comment_match.group(1).strip()
    return line
