# jacoco_filter/model.py

from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Counter:
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
    name: str
    desc: str
    line: Optional[str]
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None

@dataclass
class Class:
    name: str
    methods: list[Method] = field(default_factory=list)
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None

@dataclass
class Package:
    name: str
    classes: list[Class] = field(default_factory=list)
    counters: list[Counter] = field(default_factory=list)
    xml_element: Any = None

@dataclass
class JacocoReport:
    packages: list[Package] = field(default_factory=list)
    xml_element: Any = None
