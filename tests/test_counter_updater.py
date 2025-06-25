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
    assert counters[1].missed == 3
    assert counters[1].covered == 7


def test_aggregate_instruction_counters():
    updater = CounterUpdater()

    m1 = DummyMethod([make_counter("INSTRUCTION", 2, 4)])
    m2 = DummyMethod([make_counter("INSTRUCTION", 1, 3)])

    # Add a parent element so .getparent() works
    parent_elem = etree.Element("class")
    parent_elem.append(m1.xml_element)
    parent_elem.append(m2.xml_element)

    result = updater._aggregate_instruction_counters([m1, m2])

    assert len(result) == 1
    agg = result[0]
    assert agg.type == "INSTRUCTION"
    assert agg.missed == 3
    assert agg.covered == 7
    assert agg.xml_element.get("type") == "INSTRUCTION"
    assert agg.xml_element.get("missed") == "3"
    assert agg.xml_element.get("covered") == "7"


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


def test_existing_instruction_counter_is_removed():
    updater = CounterUpdater()

    # Create method element
    method_elem = etree.Element("method")

    # Create class element (parent), and insert old counter + method
    parent_elem = etree.Element("class")
    old_counter_elem = etree.Element("counter", type="INSTRUCTION", missed="999", covered="999")
    parent_elem.append(old_counter_elem)
    parent_elem.append(method_elem)

    # Create method with XML and instruction counter
    method = DummyMethod([make_counter("INSTRUCTION", 2, 3)])
    method.xml_element = method_elem  # attach actual element

    # Now method.xml_element.getparent() returns parent_elem automatically
    result = updater._aggregate_instruction_counters([method])

    # Ensure the old counter was removed
    counters = parent_elem.findall("counter")
    assert len(counters) == 1
    assert counters[0].get("type") == "INSTRUCTION"
    assert counters[0].get("missed") == "2"
    assert counters[0].get("covered") == "3"
    assert counters[0] is result[0].xml_element
