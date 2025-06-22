# jacoco_filter/filter_engine.py

from fnmatch import fnmatchcase
from jacoco_filter.model import JacocoReport, Package, Class, Method
from jacoco_filter.rules import FilterRule, ScopeEnum


class FilterEngine:
    def __init__(self, rules: list[FilterRule]):
        self.rules = rules
        self.stats = {"methods_removed": 0, "classes_removed": 0}

    def apply(self, report: JacocoReport):
        for package in report.packages:
            remaining_classes = []

            for cls in package.classes:
                fqcn = cls.name.replace("/", ".")
                simple_class_name = fqcn.split(".")[-1]
                sourcefilename = getattr(
                    cls, "sourcefilename", cls.xml_element.get("sourcefilename", "")
                )

                class_attrs = {
                    "fully_qualified_classname": fqcn,
                    "sourcefilename": sourcefilename,
                }

                # Check if class should be removed by class or file rule
                if self._matches(class_attrs, "class") or self._matches(
                    class_attrs, "file"
                ):
                    print(
                        f"[DEBUG] Removing class due to rule: {fqcn} ({sourcefilename})"
                    )
                    self.stats["classes_removed"] += 1
                    parent_elem = cls.xml_element.getparent()
                    if parent_elem is not None:
                        parent_elem.remove(cls.xml_element)
                    continue

                # Process methods in class
                remaining_methods = []
                for method in cls.methods:
                    method_attrs = {
                        "fully_qualified_classname": fqcn,
                        "simple_class_name": simple_class_name,
                        "method_name": method.name,
                    }

                    if self._matches(method_attrs, "method"):
                        print(
                            f"[DEBUG] Removing method due to rule: {fqcn}#{method.name}"
                        )
                        self.stats["methods_removed"] += 1
                        if (
                            cls.xml_element is not None
                            and method.xml_element is not None
                        ):
                            cls.xml_element.remove(method.xml_element)
                        continue

                    remaining_methods.append(method)

                cls.methods = remaining_methods
                remaining_classes.append(cls)

            package.classes = remaining_classes

    def _matches(self, target: dict, scope: str) -> bool:
        for rule in self.rules:
            if rule.scope == scope and rule.matches(target):
                print(
                    f"[DEBUG] Matching rule '{rule.pattern}' on scope '{scope}' => matched"
                )
                return True
        return False
