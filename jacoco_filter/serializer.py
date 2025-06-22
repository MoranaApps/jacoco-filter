# jacoco_filter/serializer.py

from pathlib import Path
from lxml import etree
from jacoco_filter.model import JacocoReport


class ReportSerializer:
    def __init__(self, report: JacocoReport):
        self.report = report

    def write_to_file(self, output_path: Path):
        tree = etree.ElementTree(self.report.xml_element)
        tree.write(
            str(output_path), encoding="utf-8", pretty_print=True, xml_declaration=True
        )
