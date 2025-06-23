"""
Parser for JaCoCo XML reports.
"""

import logging

from pathlib import Path
from lxml import etree
from jacoco_filter.model import JacocoReport, Package, Class, Method, Counter


logger = logging.getLogger(__name__)


class JacocoParser:
    """
    A parser for JaCoCo XML reports.
    """

    def __init__(self, input_path: Path):
        self.input_path = input_path

    def parse(self) -> JacocoReport:
        """
        Parses the JaCoCo XML report from the given input path.

        Returns:
            JacocoReport: The parsed JaCoCo report containing packages, classes, methods, and counters.
        """
        logger.info("Parsing %s", self.input_path)

        tree = etree.parse(str(self.input_path))
        root = tree.getroot()

        report = JacocoReport(xml_element=root)

        for pkg_elem in root.findall("package"):
            pkg = Package(xml_element=pkg_elem, name=pkg_elem.get("name"))
            report.packages.append(pkg)

            for cls_elem in pkg_elem.findall("class"):
                cls = Class(xml_element=cls_elem, name=cls_elem.get("name"))
                pkg.classes.append(cls)

                for meth_elem in cls_elem.findall("method"):
                    meth = Method(
                        xml_element=meth_elem,
                        name=meth_elem.get("name"),
                        desc=meth_elem.get("desc"),
                        line=meth_elem.get("line"),
                    )
                    cls.methods.append(meth)

                    for counter_elem in meth_elem.findall("counter"):
                        counter = Counter.from_xml(counter_elem)
                        meth.counters.append(counter)

                for counter_elem in cls_elem.findall("counter"):
                    counter = Counter.from_xml(counter_elem)
                    cls.counters.append(counter)

            for counter_elem in pkg_elem.findall("counter"):
                counter = Counter.from_xml(counter_elem)
                pkg.counters.append(counter)

        return report
