from enum import Enum

import pytest
from jacoco_filter.rules import (
    FilterRule,
    ScopeEnum,
    load_filter_rules,
    strip_comment
)

# ---------- ScopeEnum ----------

def test_scope_enum_has_value():
    assert ScopeEnum.has_value("file") is True
    assert ScopeEnum.has_value("method") is True
    assert ScopeEnum.has_value("banana") is False

# ---------- FilterRule.parse ----------

def test_parse_valid_file_rule():
    rule = FilterRule.parse("file:**/generated/**")
    assert rule.scope == ScopeEnum.FILE
    assert rule.pattern == "**/generated/**"

def test_parse_valid_method_rule():
    rule = FilterRule.parse("method:MyClass#get*")
    assert rule.scope == ScopeEnum.METHOD
    assert rule.target_class_pattern == "MyClass"
    assert rule.target_method_pattern == "get*"

def test_parse_method_rule_without_class():
    rule = FilterRule.parse("method:getValue*")
    assert rule.scope == ScopeEnum.METHOD
    assert rule.target_class_pattern is None
    assert rule.target_method_pattern == "getValue*"

def test_parse_invalid_scope_raises():
    with pytest.raises(ValueError, match="Invalid scope 'banana'"):
        FilterRule.parse("banana:somePattern")

def test_parse_missing_colon_raises():
    with pytest.raises(ValueError, match="Missing ':' in rule"):
        FilterRule.parse("invalidrule")

def test_parse_empty_pattern_raises():
    with pytest.raises(ValueError, match="Empty pattern in rule"):
        FilterRule.parse("class:   ")

# ---------- FilterRule.is_valid_line ----------

@pytest.mark.parametrize("line, expected", [
    ("file:some/path", True),
    ("method:MyClass#get*", True),
    ("# comment", False),
    ("   ", False),
    ("nonsense", False),
])
def test_is_valid_line(line, expected):
    assert FilterRule.is_valid_line(line) == expected

# ---------- FilterRule.matches ----------

def test_file_rule_match():
    rule = FilterRule(scope=ScopeEnum.FILE, pattern="**/gen/**")
    assert rule.matches({"sourcefilename": "src/gen/My.java"}) is True
    assert rule.matches({"sourcefilename": "src/main/My.java"}) is False

def test_class_rule_match():
    rule = FilterRule(scope=ScopeEnum.CLASS, pattern="com.example.*")
    assert rule.matches({"fully_qualified_classname": "com.example.MyClass"}) is True
    assert rule.matches({"fully_qualified_classname": "org.other.MyClass"}) is False

def test_method_rule_matches_fqcn_and_method():
    rule = FilterRule(scope=ScopeEnum.METHOD, pattern="MyClass#get*")
    target = {
        "method_name": "getValue",
        "fully_qualified_classname": "com.example.MyClass",
        "simple_class_name": "MyClass"
    }
    assert rule.matches(target) is True

def test_method_rule_no_class_match():
    rule = FilterRule(scope=ScopeEnum.METHOD, pattern="OtherClass#doStuff")
    target = {
        "method_name": "doStuff",
        "fully_qualified_classname": "com.example.MyClass",
        "simple_class_name": "MyClass"
    }
    assert rule.matches(target) is False

def test_method_rule_missing_key():
    rule = FilterRule(scope=ScopeEnum.METHOD, pattern="get*")
    with pytest.raises(KeyError, match="Missing key 'method_name'"):
        rule.matches({})  # empty target

# ---------- strip_comment ----------

@pytest.mark.parametrize("line, expected", [
    ("method:MyClass#get*", "method:MyClass#get*"),
    ("method:MyClass#get*   # comment", "method:MyClass#get*"),
    ("   # comment only", ""),
    ("", ""),
])
def test_strip_comment(line, expected):
    assert strip_comment(line) == expected

# ---------- load_filter_rules ----------

def test_load_filter_rules_valid(tmp_path):
    rule_file = tmp_path / "rules.txt"
    rule_file.write_text("""
        # this is a comment
        class:com.example.*
        method:MyClass#get*
    """)

    rules = load_filter_rules(rule_file)
    assert len(rules) == 2
    assert rules[0].scope == ScopeEnum.CLASS
    assert rules[1].scope == ScopeEnum.METHOD

def test_load_filter_rules_invalid_scope(tmp_path):
    rule_file = tmp_path / "rules.txt"
    rule_file.write_text("banana:foo")

    with pytest.raises(ValueError, match="Unsupported rule scope 'banana'"):
        load_filter_rules(rule_file)

def test_load_filter_rules_multiple_colons(tmp_path):
    rule_file = tmp_path / "rules.txt"
    rule_file.write_text("method:MyClass#get:*")

    with pytest.raises(ValueError, match="Multiple colons found"):
        load_filter_rules(rule_file)

def test_matches_fallback_scope_returns_false():
    class DummyScope(str, Enum):
        UNKNOWN = "unknown"

    rule = FilterRule(scope=DummyScope.UNKNOWN, pattern="*something*")  # type: ignore
    assert rule.matches({"some_key": "value"}) is False

def test_load_filter_rules_invalid_format(tmp_path):
    file = tmp_path / "rules.txt"
    file.write_text("invalid_rule_line_without_colon")

    with pytest.raises(ValueError, match="Invalid rule format on line 1: 'invalid_rule_line_without_colon'"):
        load_filter_rules(file)

def test_load_filter_rules_empty_pattern(tmp_path):
    file = tmp_path / "rules.txt"
    file.write_text("class:")

    with pytest.raises(ValueError, match="Empty pattern on line 1"):
        load_filter_rules(file)

