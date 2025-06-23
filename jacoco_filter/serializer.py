"""
This module provides functionality to serialize a JacocoReport object to an XML file.
"""

from pathlib import Path
from lxml import etree
from jacoco_filter.model import JacocoReport


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
        tree = etree.ElementTree(self.report.xml_element)
        tree.write(
            str(output_path), encoding="utf-8", pretty_print=True, xml_declaration=True
        )
