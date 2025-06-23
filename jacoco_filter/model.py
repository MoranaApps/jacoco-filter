"""
This module defines data classes to represent the structure of a JaCoCo XML report.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Counter:
    """
    Represents a coverage counter in a JaCoCo report.
    """
    type: str
    missed: int
    covered: int
    xml_element: Any

    @classmethod
    def from_xml(cls, elem):
        return cls(
            type=elem.get("type"),
            missed=int(elem.get("missed")),
            covered=int(elem.get("covered")),
            xml_element=elem,
        )


@dataclass
class Method:
    """
    Represents a method in a JaCoCo report.
    """
    name: str
    desc: str
    line: Optional[str]
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None


@dataclass
class Class:
    """
    Represents a class in a JaCoCo report.
    """
    name: str
    methods: list[Method] = field(default_factory=list)
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None


@dataclass
class Package:
    """
    Represents a package in a JaCoCo report.
    """
    name: str
    classes: list[Class] = field(default_factory=list)
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None


@dataclass
class JacocoReport:
    packages: list[Package] = field(default_factory=list)
    xml_element: Any = None
