# jacoco_filter/filter_engine.py

from fnmatch import fnmatchcase
from jacoco_filter.model import JacocoReport, Package, Class, Method
from jacoco_filter.rules import FilterRule


class FilterEngine:
    def __init__(self, rules: list[FilterRule]):
        self.rules = rules
        self.stats = {
            "methods_removed": 0,
            "classes_removed": 0
        }

    def apply(self, report: JacocoReport):
        for package in report.packages:
            remaining_classes = []

            for cls in package.classes:
                if self._matches(cls.name, "class"):
                    print(f"[DEBUG] Removing class: {cls.name}")
                    self.stats["classes_removed"] += 1
                    # Remove XML element
                    parent_elem = cls.xml_element.getparent()
                    if parent_elem is not None:
                        parent_elem.remove(cls.xml_element)
                    continue

                remaining_methods = []
                for method in cls.methods:
                    if self._matches(method.name, "method"):
                        print(f"[DEBUG] Removing method: {method.name} in class {cls.name}")
                        self.stats["methods_removed"] += 1
                        # Remove XML element
                        if cls.xml_element is not None:
                            method_elem = method.xml_element
                            if method_elem is not None:
                                cls.xml_element.remove(method_elem)
                        continue
                    remaining_methods.append(method)

                cls.methods = remaining_methods
                remaining_classes.append(cls)

            package.classes = remaining_classes

    def _matches(self, name: str, scope: str) -> bool:
        for rule in self.rules:
            if rule.scope == scope:
                match = fnmatchcase(name, rule.pattern)
                print(f"[DEBUG] Matching {scope} '{name}' against '{rule.pattern}' => {match}")
                if match:
                    return True
        return False