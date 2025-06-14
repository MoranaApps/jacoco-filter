# jacoco_filter/parser.py

from lxml import etree
from pathlib import Path
from jacoco_filter.model import JacocoReport, Package, Class, Method, Counter


class JacocoParser:
    def __init__(self, xml_path: Path):
        self.xml_path = xml_path

    def parse(self) -> JacocoReport:
        tree = etree.parse(str(self.xml_path))
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
                        line=meth_elem.get("line")
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
