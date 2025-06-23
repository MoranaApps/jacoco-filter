import logging
import os
import pytest
from jacoco_filter.logging_config import setup_logging


def test_default_logging_level(caplog):
    caplog.set_level(logging.INFO)
    setup_logging()

    assert "Logging configuration set up." in caplog.text
    assert "Debug logging enabled." not in caplog.text
    assert "Debug mode enabled by CI runner." not in caplog.text


def test_verbose_logging_enables_debug(caplog):
    caplog.set_level(logging.DEBUG)
    setup_logging(is_verbose=True)

    assert "Logging configuration set up." in caplog.text
    assert "Debug logging enabled." in caplog.text


def test_runner_debug_env_variable(monkeypatch, caplog):
    monkeypatch.setenv("RUNNER_DEBUG", "1")
    caplog.set_level(logging.DEBUG)
    setup_logging(is_verbose=False)

    assert "Logging configuration set up." in caplog.text
    assert "Debug mode enabled by CI runner." in caplog.text


def test_combined_verbose_and_runner_debug(monkeypatch, caplog):
    monkeypatch.setenv("RUNNER_DEBUG", "1")
    caplog.set_level(logging.DEBUG)
    setup_logging(is_verbose=True)

    assert "Debug logging enabled." in caplog.text
    assert "Debug mode enabled by CI runner." in caplog.text
