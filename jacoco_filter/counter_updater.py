# jacoco_filter/counter_updater.py

from jacoco_filter.model import JacocoReport, Package, Class, Method, Counter


class CounterUpdater:
    NON_INSTRUCTION_TYPES = {"LINE", "METHOD", "CLASS", "BRANCH", "COMPLEXITY"}

    def apply(self, report: JacocoReport):
        for package in report.packages:
            # Clean non-instruction counters at package level too (optional)
            self._clean_non_instruction_counters(package.counters)

            for cls in package.classes:
                self._clean_non_instruction_counters(cls.counters)

                for method in cls.methods:
                    self._clean_non_instruction_counters(method.counters)

                cls.counters = self._aggregate_instruction_counters(cls.methods)

            package.counters = self._aggregate_instruction_counters(package.classes)

        report.counters = self._aggregate_instruction_counters(report.packages)

    def _clean_non_instruction_counters(self, counters: list[Counter]):
        for counter in counters:
            if counter.type in self.NON_INSTRUCTION_TYPES:
                counter.missed = 0
                counter.covered = 0
                # Update original XML as well
                counter.xml_element.set("missed", "0")
                counter.xml_element.set("covered", "0")

    def _aggregate_instruction_counters(self, children: list) -> list[Counter]:
        total_missed = 0
        total_covered = 0

        for item in children:
            for counter in item.counters:
                if counter.type == "INSTRUCTION":
                    total_missed += counter.missed
                    total_covered += counter.covered

        # Create new Counter and XML element
        if children and hasattr(children[0], "xml_element"):
            import lxml.etree as ET

            parent_elem = children[0].xml_element.getparent()

            if parent_elem is not None:
                # Remove all existing instruction counters
                for old_counter in parent_elem.findall("counter"):
                    if old_counter.get("type") == "INSTRUCTION":
                        parent_elem.remove(old_counter)

                # Create and insert the new one
                new_elem = ET.Element(
                    "counter",
                    type="INSTRUCTION",
                    missed=str(total_missed),
                    covered=str(total_covered),
                )
                parent_elem.append(new_elem)
        else:
            new_elem = None

        return [
            Counter(
                type="INSTRUCTION",
                missed=total_missed,
                covered=total_covered,
                xml_element=new_elem,
            )
        ]
