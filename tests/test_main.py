import logging
import sys
from jacoco_filter.cli import logger


def test_main_success(monkeypatch, tmp_path, caplog):
    from jacoco_filter.rules import FilterRule, ScopeEnum
    from jacoco_filter.__main__ import main

    # 👇 capture INFO logs
    caplog.set_level(logging.INFO)

    # Create dummy XML file
    dummy_input = tmp_path / "jacoco.xml"
    dummy_input.write_text("<report><package name='pkg'/></report>")

    monkeypatch.chdir(tmp_path)

    dummy_args = {
        "inputs": ["*.xml"],
        "exclude_paths": [],
        "rules": [FilterRule(scope=ScopeEnum.CLASS, pattern="*")],
        "verbose": True,
    }

    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--inputs", "*.xml"])
    monkeypatch.setattr("jacoco_filter.cli.parse_arguments", lambda: dummy_args)
    monkeypatch.setattr("jacoco_filter.logging_config.setup_logging", lambda verbose: None)
    monkeypatch.setattr("jacoco_filter.cli.apply_excludes", lambda paths, excludes, root: paths)

    dummy_report = object()

    class DummyParser:
        def __init__(self, path): pass
        def parse(self): return dummy_report

    class DummyEngine:
        def __init__(self, rules): self.stats = {"classes_removed": 1, "methods_removed": 2}
        def apply(self, report): pass

    class DummyUpdater:
        def apply(self, report): pass

    class DummySerializer:
        def __init__(self, report): self.report = report
        def write_to_file(self, path): path.write_text("<filtered/>")

    monkeypatch.setattr("jacoco_filter.parser.JacocoParser", DummyParser)
    monkeypatch.setattr("jacoco_filter.filter_engine.FilterEngine", DummyEngine)
    monkeypatch.setattr("jacoco_filter.counter_updater.CounterUpdater", lambda: DummyUpdater())
    monkeypatch.setattr("jacoco_filter.serializer.ReportSerializer", DummySerializer)

    # 🏁 Run main
    main()

    # ✅ Check logs
    assert any("jacoco-filter started" in record.message for record in caplog.records)
    assert any("Removed" in record.message and "class" in record.message for record in caplog.records)

    # ✅ Check file was written
    assert (tmp_path / "jacoco.filtered.xml").exists()


def test_main_failure(monkeypatch):
    # ✅ Clean sys.argv
    monkeypatch.setattr(sys, "argv", ["jacoco-filter"])
    monkeypatch.setattr("jacoco_filter.cli.parse_arguments", lambda: (_ for _ in ()).throw(RuntimeError("Boom")))
    monkeypatch.setattr("jacoco_filter.logging_config.setup_logging", lambda verbose: None)

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 1


import pytest
from jacoco_filter.__main__ import main
from jacoco_filter.rules import FilterRule, ScopeEnum

def test_main_no_inputs_after_exclude(monkeypatch):
    dummy_args = {
        "inputs": ["*.xml"],
        "exclude_paths": [],
        "rules": [FilterRule(scope=ScopeEnum.CLASS, pattern="*")],
        "verbose": False,
    }

    # Fake sys.argv to avoid argparse interfering
    monkeypatch.setattr(sys, "argv", ["jacoco-filter", "--inputs", "*.xml"])
    monkeypatch.setattr("jacoco_filter.cli.parse_arguments", lambda: dummy_args)
    monkeypatch.setattr("jacoco_filter.logging_config.setup_logging", lambda verbose: None)
    monkeypatch.setattr("jacoco_filter.cli.resolve_globs", lambda patterns, root: ["file1.xml", "file2.xml"])
    monkeypatch.setattr("jacoco_filter.cli.apply_excludes", lambda paths, excludes, root: [])  # all files excluded

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
