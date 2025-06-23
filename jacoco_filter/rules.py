"""
This module defines the FilterRule class and related functionality for parsing and applying filter rules
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from fnmatch import fnmatchcase
from typing import Optional


logger = logging.getLogger(__name__)


class ScopeEnum(str, Enum):
    """
    Enum representing the scope of a filter rule.
    """

    FILE = "file"
    CLASS = "class"
    METHOD = "method"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


@dataclass
class FilterRule:
    """
    Represents a filter rule for matching files, classes, or methods based on patterns.
    """

    scope: ScopeEnum  # "file", "class", or "method"
    pattern: str
    target_class_pattern: Optional[str] = field(init=False, default=None)
    target_method_pattern: Optional[str] = field(init=False, default=None)

    def __post_init__(self):
        """
        Post-initialization processing to split the pattern into class and method patterns if applicable.

        Returns:
            None
        """
        if self.scope == ScopeEnum.METHOD:
            if "#" in self.pattern:
                self.target_class_pattern, self.target_method_pattern = self.pattern.split("#", 1)
            else:
                self.target_class_pattern = None
                self.target_method_pattern = self.pattern

    def matches(self, target: dict) -> bool:
        """
        Checks if the target matches the filter rule based on its scope and pattern.

        Parameters:
            target (dict): A dictionary representing the target to match against the rule.
        Returns:
            bool: True if the target matches the rule, False otherwise.
        Raises:
            KeyError: If a required key is missing in the target dictionary.
        """
        try:
            match self.scope:
                case ScopeEnum.FILE:
                    return fnmatchcase(target["sourcefilename"], self.pattern)

                case ScopeEnum.CLASS:
                    return fnmatchcase(target["fully_qualified_classname"], self.pattern)

                case ScopeEnum.METHOD:
                    method_name = target["method_name"]
                    fqcn = target.get("fully_qualified_classname", "")
                    simple_class = target.get("simple_class_name", fqcn.split(".")[-1] if fqcn else "")

                    logger.debug(
                        "METHOD: fqcn=%s, simple_class=%s, method=%s",
                        fqcn,
                        simple_class,
                        method_name,
                    )
                    logger.debug(
                        "Rule: class_pattern=%s, method_pattern=%s",
                        self.target_class_pattern,
                        self.target_method_pattern,
                    )

                    if self.target_class_pattern:
                        class_match = fnmatchcase(fqcn, self.target_class_pattern) or fnmatchcase(
                            simple_class, self.target_class_pattern
                        )

                        if not class_match:
                            logger.debug(
                                "Rule '%s' did not match class '%s' or '%s'",
                                self.pattern,
                                fqcn,
                                simple_class,
                            )
                            return False

                    matched = fnmatchcase(method_name, self.target_method_pattern)
                    logger.debug(
                        "Matching method '%s' with rule '%s' => %s",
                        method_name,
                        self.pattern,
                        matched,
                    )
                    return matched

                case _:
                    return False

        except KeyError as e:
            raise KeyError(f"Missing key '{e.args[0]}' in target dict for rule: {self.scope}:{self.pattern}") from e

    @staticmethod
    def is_valid_line(line: str) -> bool:
        """
        Checks if a line is a valid filter rule line.

        Parameters:
            line (str): The line to check.
        Returns:
            bool: True if the line is a valid filter rule, False otherwise.
        """
        line = line.strip()
        return bool(line) and not line.startswith("#") and ":" in line and any(scope in line for scope in ScopeEnum)

    @classmethod
    def parse(cls, line: str) -> "FilterRule":
        """
        Parses a line into a FilterRule object.

        Parameters:
            cls: The class to instantiate.
            line (str): The line to parse.
        Returns:
            FilterRule: An instance of FilterRule.
        Raises:
            ValueError: If the line is not a valid filter rule.
        """
        if ":" not in line:
            raise ValueError(f"Missing ':' in rule: '{line}'")

        scope, pattern = line.split(":", 1)
        scope = scope.strip()
        pattern = pattern.strip()

        if not ScopeEnum.has_value(scope):
            raise ValueError(f"Invalid scope '{scope}' in rule: '{line}'")

        if not pattern:
            raise ValueError(f"Empty pattern in rule: '{line}'")

        return cls(ScopeEnum(scope), pattern)


def load_filter_rules(path: Path) -> list[FilterRule]:
    """
    Loads filter rules from a file at the given path.

    Parameters:
        path (Path): The path to the file containing filter rules.
    Returns:
        list[FilterRule]: A list of FilterRule objects parsed from the file.
    Raises:
        ValueError: If the file contains invalid rule formats.
    """
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
