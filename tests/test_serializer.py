import pytest
from pathlib import Path
from lxml import etree
from jacoco_filter.serializer import ReportSerializer


class DummyReport:
    def __init__(self):
        self.xml_element = etree.Element("report", name="dummy")


def test_write_to_file_creates_valid_xml(tmp_path):
    report = DummyReport()
    serializer = ReportSerializer(report)

    output_path = tmp_path / "report.xml"
    serializer.write_to_file(output_path)

    assert output_path.exists()

    # Validate content
    tree = etree.parse(str(output_path))
    root = tree.getroot()

    assert root.tag == "report"
    assert root.attrib["name"] == "dummy"
