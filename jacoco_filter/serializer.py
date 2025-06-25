"""
This module provides functionality to serialize a JacocoReport object to an XML file.
"""
import logging
from pathlib import Path
from lxml import etree
from jacoco_filter.model import JacocoReport


logger = logging.getLogger(__name__)


class ReportSerializer:
    """
    A class to serialize a JacocoReport object to an XML file.
    """

    def __init__(self, report: JacocoReport):
        self.report = report

    def write_to_file(self, output_path: Path):
        """
        Serializes the JacocoReport object to an XML file.
        Parameters:
            output_path (Path): The path where the XML file will be saved.
        Returns:
            None
        """

        # DEBUG
        for package in self.report.packages:
            for sourcefile in package.sourcefiles:
                logger.debug("Source file '%s' counters: %s", sourcefile.name, sourcefile.counters)

        tree = etree.ElementTree(self.report.xml_element)
        tree.write(str(output_path), encoding="utf-8", pretty_print=True, xml_declaration=True)
