import pytest
from lxml import etree

from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.rules import FilterRule, ScopeEnum
from jacoco_filter.model import JacocoReport, Counter


# --- Dummies and helpers ---

class DummyMethod:
    def __init__(self, name):
        self.name = name
        self.xml_element = etree.Element("method", name=name)

class DummyClass:
    def __init__(self, name, methods, sourcefilename="src/Example.java"):
        self.name = name
        self.methods = methods
        self.xml_element = etree.Element("class", name=name)
        self.sourcefilename = sourcefilename
        for method in methods:
            self.xml_element.append(method.xml_element)

class DummyPackage:
    def __init__(self, classes):
        self.classes = classes
        self.xml_element = etree.Element("package", name="pkg")
        for cls in classes:
            self.xml_element.append(cls.xml_element)


# --- Tests ---

def test_removes_class_matching_class_rule():
    rule = FilterRule(scope=ScopeEnum.CLASS, pattern="com.example.MyClass")
    rule.matches = lambda target: target["fully_qualified_classname"] == "com.example.MyClass"

    cls = DummyClass("com/example/MyClass", [DummyMethod("doSomething")])
    pkg = DummyPackage([cls])
    report = JacocoReport(xml_element=etree.Element("report"))
    report.packages = [pkg]

    engine = FilterEngine([rule])
    engine.apply(report)

    assert pkg.classes == []  # class removed
    assert engine.stats["classes_removed"] == 1


def test_removes_method_matching_method_rule():
    rule = FilterRule(scope=ScopeEnum.METHOD, pattern="*#removeMe")
    rule.target_class_pattern = None
    rule.target_method_pattern = "removeMe"
    rule.matches = lambda target: target["method_name"] == "removeMe"

    method1 = DummyMethod("keepMe")
    method2 = DummyMethod("removeMe")
    cls = DummyClass("com/example/Utility", [method1, method2])
    pkg = DummyPackage([cls])
    report = JacocoReport(xml_element=etree.Element("report"))
    report.packages = [pkg]

    engine = FilterEngine([rule])
    engine.apply(report)

    assert len(cls.methods) == 1
    assert cls.methods[0].name == "keepMe"
    assert engine.stats["methods_removed"] == 1


def test_removes_class_matching_file_rule():
    rule = FilterRule(scope=ScopeEnum.FILE, pattern="src/Example.java")
    rule.matches = lambda target: target["sourcefilename"] == "src/Example.java"

    cls = DummyClass("com/example/Helper", [DummyMethod("init")])
    pkg = DummyPackage([cls])
    report = JacocoReport(xml_element=etree.Element("report"))
    report.packages = [pkg]

    engine = FilterEngine([rule])
    engine.apply(report)

    assert pkg.classes == []
    assert engine.stats["classes_removed"] == 1


def test_does_not_remove_if_no_match():
    rule = FilterRule(scope=ScopeEnum.CLASS, pattern="NonMatchingClass")
    rule.matches = lambda target: False

    cls = DummyClass("com/example/Keep", [DummyMethod("method")])
    pkg = DummyPackage([cls])
    report = JacocoReport(xml_element=etree.Element("report"))
    report.packages = [pkg]

    engine = FilterEngine([rule])
    engine.apply(report)

    assert pkg.classes == [cls]
    assert cls.methods[0].name == "method"
    assert engine.stats["classes_removed"] == 0
    assert engine.stats["methods_removed"] == 0


def test_matches_applies_scope_filter():
    rule1 = FilterRule(scope=ScopeEnum.CLASS, pattern="Match")
    rule2 = FilterRule(scope=ScopeEnum.METHOD, pattern="Ignore")
    rule1.matches = lambda target: True
    rule2.matches = lambda target: True  # should be skipped due to wrong scope

    engine = FilterEngine([rule1, rule2])
    assert engine._matches({"some": "thing"}, "class") is True
    assert engine._matches({"some": "thing"}, "file") is False
