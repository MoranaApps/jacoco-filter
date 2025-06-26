import pytest
from lxml import etree
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.model import Counter, JacocoReport


class DummyMethod:
    def __init__(self, counters, name="m"):
        self.counters = counters
        self.xml_element = etree.Element("method", name=name)


class DummyClass:
    def __init__(self, methods, counters, name="C", source_filename="S"):
        self.methods = methods
        self.name = name
        self.source_filename = source_filename
        self.counters = counters
        self.xml_element = etree.Element("class", name=name)
        for m in methods:
            self.xml_element.append(m.xml_element)


class DummySourceFile:
    def __init__(self, counters, name="S"):
        self.counters = counters
        self.name = name
        self.xml_element = etree.Element("sourcefile", name=name)


class DummyPackage:
    def __init__(self, classes, sourcefiles, counters, name="p"):
        self.classes = classes
        self.sourcefiles = sourcefiles
        self.counters = counters
        self.xml_element = etree.Element("package", name=name)
        for c in classes:
            self.xml_element.append(c.xml_element)


def make_counter(counter_type, missed, covered):
    el = etree.Element("counter", type=counter_type, missed=str(missed), covered=str(covered))
    return Counter(type=counter_type, missed=missed, covered=covered, xml_element=el)


def test_clean_non_instruction_counters():
    updater = CounterUpdater()

    counters = [
        make_counter("LINE", 5, 10),
        make_counter("INSTRUCTION", 3, 7),
    ]
    updater._clean_non_instruction_counters(counters)

    assert counters[0].missed == 0
    assert counters[0].covered == 0
    assert counters[0].xml_element.get("missed") == "0"
    assert counters[0].xml_element.get("covered") == "0"

    # Instruction counters should be untouched
    assert counters[1].missed == 0
    assert counters[1].covered == 0


def test_aggregate_instruction_counters_basic():
    updater = CounterUpdater()

    m1 = DummyMethod([make_counter("INSTRUCTION", 2, 4)], name="m1")
    m2 = DummyMethod([make_counter("INSTRUCTION", 3, 1)], name="m2")
    cls = DummyClass(methods=[m1, m2], counters=[
        make_counter("INSTRUCTION", 0, 0)
    ], name="C")

    # Attach class XML to simulate a real DOM
    parent_elem = cls.xml_element
    parent_elem.append(m1.xml_element)
    parent_elem.append(m2.xml_element)

    updater._aggregate_instruction_counters(parent=cls, children=cls.methods)

    assert len(cls.counters) == 1
    counter = cls.counters[0]

    assert counter.type == "INSTRUCTION"
    assert counter.missed == 5  # 2 + 3
    assert counter.covered == 5  # 4 + 1
    assert counter.xml_element.get("missed") == "5"
    assert counter.xml_element.get("covered") == "5"

    xml_counters = parent_elem.findall("counter")
    assert len(xml_counters) == 1
    assert xml_counters[0].get("type") == "INSTRUCTION"


def test_apply_updates_all_levels():
    updater = CounterUpdater()

    m1 = DummyMethod([
        make_counter("INSTRUCTION", 5, 10),
        make_counter("LINE", 4, 4),
    ])
    m2 = DummyMethod([
        make_counter("INSTRUCTION", 3, 7),
        make_counter("METHOD", 2, 2),
    ])
    c1 = DummyClass([m1, m2], counters=[
        make_counter("BRANCH", 1, 1),
        make_counter("INSTRUCTION", 0, 0),
    ])
    s1 = DummySourceFile(counters=[
        make_counter("BRANCH", 1, 1),
        make_counter("INSTRUCTION", 0, 0),
    ])
    p1 = DummyPackage([c1], [s1], counters=[
        make_counter("CLASS", 1, 1),
        make_counter("INSTRUCTION", 0, 0),
    ])

    report = JacocoReport(xml_element=etree.Element("report"))
    report.packages = [p1]
    report.counters.append(p1.counters[0])
    report.counters.append(p1.counters[1])

    # Add package XML structure
    report.xml_element.append(p1.xml_element)

    updater.apply(report)

    # Report-level aggregated counters should sum all instruction counters
    assert len(report.counters) == 2
    assert report.counters[1].type == "INSTRUCTION"
    assert report.counters[1].missed == 8
    assert report.counters[1].covered == 17

    # All non-INSTRUCTION counters should be zeroed
    for pkg in report.packages:
        for counter in pkg.counters:
            if counter.type != "INSTRUCTION":
                assert counter.missed == 0
                assert counter.covered == 0
        for cls in pkg.classes:
            for counter in cls.counters:
                if counter.type != "INSTRUCTION":
                    assert counter.missed == 0
                    assert counter.covered == 0


def test_aggregate_instruction_counters_removes_old_xml():
    updater = CounterUpdater()

    # Method with real values
    method = DummyMethod([make_counter("INSTRUCTION", 2, 2)], name="get")
    # DummyClass with an old counter that should be replaced
    old_counter = make_counter("INSTRUCTION", 999, 999)
    cls = DummyClass([method], counters=[old_counter], name="C")

    # Attach all XML properly
    cls.xml_element.append(method.xml_element)
    cls.xml_element.append(old_counter.xml_element)

    # Check the initial state
    assert len(cls.xml_element.findall("counter")) == 1

    updater._aggregate_instruction_counters(parent=cls, children=cls.methods)

    # Ensure the XML counter was replaced
    xml_counters = cls.xml_element.findall("counter")
    assert len(xml_counters) == 1
    updated_elem = xml_counters[0]
    assert updated_elem.get("type") == "INSTRUCTION"
    assert updated_elem.get("missed") == "2"
    assert updated_elem.get("covered") == "2"

    # Ensure the model Counter is updated
    assert cls.counters[0].missed == 2
    assert cls.counters[0].covered == 2
    assert cls.counters[0].xml_element is updated_elem
