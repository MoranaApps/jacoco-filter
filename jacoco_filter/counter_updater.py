"""
This module provides functionality to update Jacoco counters in a report.
"""
import logging

import lxml.etree as ET

from jacoco_filter.model import JacocoReport, Counter


logger = logging.getLogger(__name__)


class CounterUpdater:
    """
    CounterUpdater is responsible for cleaning non-instruction counters
    """

    NON_INSTRUCTION_TYPES = {"LINE", "METHOD", "CLASS", "BRANCH", "COMPLEXITY"}

    def apply(self, report: JacocoReport):
        """
        Apply the counter updates to the Jacoco report.

        Parameters:
            report (JacocoReport): The Jacoco report to update.
        Returns:
            None
        """
        self._clean_non_instruction_counters(report.counters)

        for package in report.packages:
            # Clean non-instruction counters at package level too (optional)
            self._clean_non_instruction_counters(package.counters)

            for sourcefile in package.sourcefiles:
                self._clean_non_instruction_counters(sourcefile.counters)

            for cls in package.classes:
                self._clean_non_instruction_counters(cls.counters)

                for method in cls.methods:
                    self._clean_non_instruction_counters(method.counters)

                cls.counters = self._aggregate_instruction_counters(cls.methods)

            for sourcefile in package.sourcefiles:
                for counter in sourcefile.counters:
                    if counter.type == "INSTRUCTION":
                        mis, cov = self._aggregate_instruction_counters_for_sourcefile(sourcefile.name, package.classes)
                        counter.missed = mis
                        counter.covered = cov

            package.counters = self._aggregate_instruction_counters(package.classes)

        for counter in report.counters:
            if counter.type == "INSTRUCTION":
                mis, cov = self._aggregate_instruction_counters_for_report(report)
                counter.missed = mis
                counter.covered = cov

    def _clean_non_instruction_counters(self, counters: list[Counter]):
        """
        Clean non-instruction counters by setting missed and covered to 0.

        Parameters:
            counters (list[Counter]): List of counters to clean.
        Returns:
            None
        """
        for counter in counters:
            if counter.type in self.NON_INSTRUCTION_TYPES:
                counter.missed = 0
                counter.covered = 0
                # Update original XML as well
                counter.xml_element.set("missed", "0")
                counter.xml_element.set("covered", "0")

    def _aggregate_instruction_counters(self, children: list) -> list[Counter]:
        """
        Aggregate instruction counters from the children elements.

        Parameters:
            children (list): List of children elements (Package, Class, Method).
        Returns:
            list[Counter]: List containing a single Counter with aggregated instruction data.
        """
        total_missed = 0
        total_covered = 0

        for item in children:
            for counter in item.counters:
                if counter.type == "INSTRUCTION":
                    total_missed += counter.missed
                    total_covered += counter.covered

        # Create new Counter and XML element
        new_elem = None

        if children and hasattr(children[0], "xml_element"):
            parent_elem = children[0].xml_element.getparent()

            if parent_elem is not None:
                for old_counter in parent_elem.findall("counter"):
                    if old_counter.get("type") == "INSTRUCTION":
                        parent_elem.remove(old_counter)

                new_elem = ET.Element(
                    "counter",
                    type="INSTRUCTION",
                    missed=str(total_missed),
                    covered=str(total_covered),
                )
                parent_elem.append(new_elem)

        return [
            Counter(
                type="INSTRUCTION",
                missed=total_missed,
                covered=total_covered,
                xml_element=new_elem,
            )
        ]

    def _aggregate_instruction_counters_for_report(self, report: JacocoReport) -> tuple:
        """
        Aggregate instruction counters for the entire report.
        During this process, it sums up all instruction counters across all packages and skip source files.

        Parameters:
            report (JacocoReport): The Jacoco report to aggregate.
        Returns:
            list[Counter]: List containing a single Counter with aggregated instruction data.
        """
        total_missed = 0
        total_covered = 0

        for package in report.packages:
            for clazz in package.classes:
                for counter in clazz.counters:
                    if counter.type == "INSTRUCTION":
                        total_missed += counter.missed
                        total_covered += counter.covered

        return total_missed, total_covered

    def _aggregate_instruction_counters_for_sourcefile(self, sourcefile: str, classes: list) -> tuple:
        """
        Aggregate instruction counters for a specific source file.

        Parameters:
            sourcefile (str): The name of the source file.
            classes (list): List of classes to aggregate counters from.
        Returns:
            list[Counter]: List containing a single Counter with aggregated instruction data.
        """
        total_missed = 0
        total_covered = 0

        for cls in classes:
            logger.debug("Processing class '%s' for source file '%s'", cls.name, sourcefile)
            if cls.source_filename == sourcefile:
                logger.debug("Class '%s' matches source file '%s'", cls.name, sourcefile)
                for counter in cls.counters:
                    if counter.type == "INSTRUCTION":
                        total_missed += counter.missed
                        total_covered += counter.covered

        logger.debug("Aggregated counters for source file '%s': missed=%d, covered=%d", sourcefile, total_missed, total_covered)

        return total_missed, total_covered

