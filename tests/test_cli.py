import sys
import pytest
from pathlib import Path

from jacoco_filter.cli import (
    load_config,
    parse_arguments,
    resolve_globs,
    apply_excludes, evaluate_parsed_arguments,
)


# ---------- load_config ----------

def test_load_config_valid(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('inputs = ["target/jacoco.xml"]\nverbose = true\n')

    config = load_config(config_file)
    assert config["inputs"] == ["target/jacoco.xml"]
    assert config["verbose"] is True


def test_load_config_missing_file(caplog):
    path = Path("/this/does/not/exist.toml")
    config = load_config(path)
    assert config == {}
    assert "Configuration file not found" in caplog.text


# ---------- resolve_globs ----------

def test_resolve_globs_finds_matching_files(tmp_path):
    (tmp_path / "target").mkdir()
    file_path = tmp_path / "target" / "jacoco.xml"
    file_path.write_text("<report/>")

    result = resolve_globs(["target/*.xml"], tmp_path)
    assert len(result) == 1
    assert result[0].name == "jacoco.xml"


def test_resolve_globs_empty_if_no_matches(tmp_path):
    result = resolve_globs(["*.none"], tmp_path)
    assert result == []


# ---------- apply_excludes ----------

def test_apply_excludes_skips_matching(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "test").mkdir()
    src_file = tmp_path / "src" / "file1.java"
    test_file = tmp_path / "test" / "file2.java"
    src_file.write_text("")
    test_file.write_text("")

    paths = [src_file, test_file]
    filtered = apply_excludes(paths, ["test/**"], tmp_path)

    assert src_file in filtered
    assert test_file not in filtered


def test_apply_excludes_skips_outside_paths(tmp_path):
    outside_path = Path("/does/not/belong/file.java")
    result = apply_excludes([outside_path], ["*"], tmp_path)
    assert result == []


# ---------- parse_arguments ----------

def test_parse_arguments_with_inputs_and_rules_file(monkeypatch, tmp_path):
    dummy_rules_file = tmp_path / "rules.txt"
    dummy_rules_file.write_text("CLASS:com.example.*")

    dummy_input_file = tmp_path / "jacoco.xml"
    dummy_input_file.write_text("<report/>")

    def dummy_load_rules(path):
        return []

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "-i", str(dummy_input_file), "-r", str(dummy_rules_file)])
    monkeypatch.setattr("jacoco_filter.cli.load_filter_rules", dummy_load_rules)
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda path: {})

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["inputs"] == [str(dummy_input_file)]
    assert result["rules"] == []
    assert result["verbose"] is False


def test_parse_arguments_inline_rules(monkeypatch):
    raw_config = {
        "inputs": ["target/a.xml"],
        "rules": ["CLASS:com.example.*"],
        "verbose": True
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda path: raw_config)
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda line: True)
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.parse", lambda line: f"PARSED({line})")

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["inputs"] == ["target/a.xml"]
    assert result["rules"] == ["PARSED(CLASS:com.example.*)"]
    assert result["verbose"] is True


def test_parse_arguments_missing_inputs(monkeypatch, caplog):
    monkeypatch.setattr(sys, "argv", ["jacoco-filter"])
    with pytest.raises(SystemExit) as e:
        evaluate_parsed_arguments(parse_arguments())

    assert e.value.code == 1
    assert "Either --inputs or a valid --config file must be provided" in caplog.text


def test_parse_arguments_no_inputs_in_config(monkeypatch, caplog):
    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: {"inputs": []})

    # avoid rule processing
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda line: False)

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["inputs"] == []
    assert "No input files provided" in caplog.text


def test_parse_arguments_uses_config_exclude_paths(monkeypatch):
    config_data = {
        "inputs": ["target/a.xml"],
        "exclude_paths": ["**/generated/**"],
        "rules": [],
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: config_data)
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda line: False)

    result = evaluate_parsed_arguments(parse_arguments())
    assert result["exclude_paths"] == ["**/generated/**"]


def test_parse_arguments_exclude_paths_from_cli(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "jacoco-filter",
            "--inputs",
            "target/jacoco.xml",
            "--exclude-paths",
            "**/test/**",
            "**/generated/**"
        ]
    )

    # Prevent config loading and rule parsing
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: {})
    monkeypatch.setattr("jacoco_filter.cli.load_filter_rules", lambda _: [])

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["exclude_paths"] == ["**/test/**", "**/generated/**"]


def test_parse_arguments_skips_comment_rules(monkeypatch, caplog):
    config_data = {
        "inputs": ["target/a.xml"],
        "rules": ["# this is a comment", "CLASS:com.example.*"]
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: config_data)
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda line: True)
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.parse", lambda line: f"PARSED({line})")

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["rules"] == ["PARSED(CLASS:com.example.*)"]
    assert "# this is a comment" not in str(result["rules"])


def test_parse_arguments_skips_invalid_rule_lines(monkeypatch, caplog):
    config_data = {
        "inputs": ["target/a.xml"],
        "rules": ["INVALID LINE"],
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: config_data)

    # Force the line to be considered invalid
    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda _: False)

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["rules"] == []
    assert "Skipping invalid rule rule: 'INVALID LINE'" in caplog.text



def test_parse_arguments_handles_parse_exception(monkeypatch, caplog):
    config_data = {
        "inputs": ["target/a.xml"],
        "rules": ["CLASS:com.example.*"],
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--config", "dummy.toml"])
    monkeypatch.setattr("jacoco_filter.cli.load_config", lambda _: config_data)

    monkeypatch.setattr("jacoco_filter.cli.FilterRule.is_valid_line", lambda _: True)

    def raise_parse_error(_):
        raise ValueError("Mock parse error")

    monkeypatch.setattr("jacoco_filter.cli.FilterRule.parse", raise_parse_error)

    result = evaluate_parsed_arguments(parse_arguments())

    assert result["rules"] == []
    assert "Failed to parse rule rule 'CLASS:com.example.*': Mock parse error" in caplog.text
