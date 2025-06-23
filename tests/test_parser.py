import pytest
from pathlib import Path
from lxml import etree
from jacoco_filter.parser import JacocoParser
from jacoco_filter.model import Counter


def create_sample_jacoco_xml(path: Path):
    xml_content = """
    <report>
      <package name="com/example">
        <class name="MyClass" sourcefilename="MyClass.java">
          <method name="doStuff" desc="()V" line="42">
            <counter type="INSTRUCTION" missed="5" covered="10"/>
          </method>
          <counter type="LINE" missed="3" covered="7"/>
        </class>
        <counter type="BRANCH" missed="1" covered="2"/>
      </package>
    </report>
    """
    path.write_text(xml_content.strip())


def test_jacoco_parser_parses_structure(tmp_path):
    xml_path = tmp_path / "jacoco.xml"
    create_sample_jacoco_xml(xml_path)

    parser = JacocoParser(xml_path)
    report = parser.parse()

    assert len(report.packages) == 1
    pkg = report.packages[0]
    assert pkg.name == "com/example"
    assert len(pkg.classes) == 1

    cls = pkg.classes[0]
    assert cls.name == "MyClass"
    assert len(cls.methods) == 1
    assert len(cls.counters) == 1
    assert cls.counters[0].type == "LINE"

    meth = cls.methods[0]
    assert meth.name == "doStuff"
    assert meth.desc == "()V"
    assert meth.line == "42"
    assert len(meth.counters) == 1

    meth_counter = meth.counters[0]
    assert isinstance(meth_counter, Counter)
    assert meth_counter.type == "INSTRUCTION"
    assert meth_counter.missed == 5
    assert meth_counter.covered == 10

    assert len(pkg.counters) == 1
    assert pkg.counters[0].type == "BRANCH"
