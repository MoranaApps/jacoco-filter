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
                    self._clean_non_instruction_counters(method.counters, False)

                # Aggregate instruction counters for each class from method values
                self._aggregate_instruction_counters(cls, cls.methods)

            for sourcefile in package.sourcefiles:
                for counter in sourcefile.counters:
                    if counter.type == "INSTRUCTION":
                        mis, cov = self._aggregate_instruction_counters_for_sourcefile(sourcefile.name, package.classes)
                        counter.missed = mis
                        counter.covered = cov

                        if counter.xml_element is not None:
                            counter.xml_element.set("missed", str(mis))
                            counter.xml_element.set("covered", str(cov))

            package.sourcefiles = self._remove_zero_coverage_sourcefiles(package)
            self._aggregate_instruction_counters(package, package.classes)

        for counter in report.counters:
            if counter.type == "INSTRUCTION":
                mis, cov = self._aggregate_instruction_counters_for_report(report)
                counter.missed = mis
                counter.covered = cov

                if counter.xml_element is not None:
                    counter.xml_element.set("missed", str(mis))
                    counter.xml_element.set("covered", str(cov))

        report.packages = self._remove_zero_coverage_packages(report)

    def _remove_zero_coverage_packages(self, report: JacocoReport) -> list:
        """
        Remove <package> elements from the XML and model if their instruction counter has 0 missed and 0 covered.

        Parameters:
            report (JacocoReport): The report containing packages.

        Returns:
            list: A list of packages with non-zero instruction coverage.
        """
        updated_packages = []

        for package in report.packages:
            for counter in package.counters:
                if counter.type == "INSTRUCTION" and counter.missed == 0 and counter.covered == 0:
                    logger.debug("Removing package '%s' with 0 instruction coverage", package.name)
                    if package.xml_element is not None:
                        parent = package.xml_element.getparent()
                        if parent is not None:
                            parent.remove(package.xml_element)
            else:
                updated_packages.append(package)

        return updated_packages

    def _remove_zero_coverage_sourcefiles(self, package) -> list:
        """
        Remove <sourcefile> elements from the XML and model if their instruction counter has 0 missed and 0 covered.

        Parameters:
            package: The package object containing sourcefiles and classes.

        Returns:
            list: A list of sourcefiles with non-zero instruction coverage.
        """
        updated_sourcefiles = []

        for sourcefile in package.sourcefiles:
            remove = False
            for counter in sourcefile.counters:
                if counter.type == "INSTRUCTION":
                    mis, cov = self._aggregate_instruction_counters_for_sourcefile(sourcefile.name, package.classes)
                    counter.missed = mis
                    counter.covered = cov

                    if counter.xml_element is not None:
                        counter.xml_element.set("missed", str(mis))
                        counter.xml_element.set("covered", str(cov))

                    if mis == 0 and cov == 0:
                        remove = True

            if remove:
                logger.debug("Removing sourcefile '%s' with 0 instruction coverage", sourcefile.name)
                if sourcefile.xml_element is not None:
                    parent = sourcefile.xml_element.getparent()
                    if parent is not None:
                        parent.remove(sourcefile.xml_element)
            else:
                updated_sourcefiles.append(sourcefile)

        return updated_sourcefiles

    def _clean_non_instruction_counters(self, counters: list[Counter], skip_instruction: bool = True):
        """
        Clean non-instruction counters by setting missed and covered to 0.

        Parameters:
            counters (list[Counter]): List of counters to clean.
        Returns:
            None
        """
        for counter in counters:
            if not skip_instruction and counter.type == "INSTRUCTION":
                continue

            counter.missed = 0
            counter.covered = 0
            # Update original XML as well
            counter.xml_element.set("missed", "0")
            counter.xml_element.set("covered", "0")

    def _aggregate_instruction_counters(self, parent, children: list):
        """
        Aggregate instruction counters from the children elements.

        Parameters:
            children (list): List of children elements (Package, Class, Method).
        Returns:
            None
        """
        total_missed = 0
        total_covered = 0

        for item in children:
            for counter in item.counters:
                if counter.type == "INSTRUCTION":
                    total_missed += counter.missed
                    total_covered += counter.covered

        # Create new Counter and XML element
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

                for counter in parent.counters:
                    if counter.type == "INSTRUCTION":
                        counter.missed = total_missed
                        counter.covered = total_covered
                        counter.xml_element = new_elem

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

        for clz in classes:
            logger.debug("Processing class '%s' for source file '%s'", clz.name, sourcefile)
            if clz.source_filename == sourcefile:
                logger.debug("Class '%s' matches source file '%s'", clz.name, sourcefile)
                for counter in clz.counters:
                    if counter.type == "INSTRUCTION":
                        total_missed += counter.missed
                        total_covered += counter.covered

        logger.debug(
            "Aggregated counters for source file '%s': missed=%d, covered=%d", sourcefile, total_missed, total_covered
        )

        return total_missed, total_covered
