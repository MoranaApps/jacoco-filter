"""
This module provides the command-line interface for jacoco-filter.
"""

import argparse
import fnmatch
import logging
import sys

from pathlib import Path
from typing import Iterable

import tomli

from jacoco_filter.rules import FilterRule, load_filter_rules

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """
    Loads the configuration from a .toml file.

    Parameters:
        config_path (Path): The path to the configuration file.
    Returns:
        dict: The loaded configuration as a dictionary.
    """
    if not config_path.exists():
        logger.error("Configuration file not found: %s.", config_path)
        return {}

    with config_path.open("rb") as f:
        logger.info("Loading configuration from %s...", config_path)
        return tomli.load(f)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments and merges them with the configuration file if provided.

    Returns:
        dict: A dictionary containing the merged configuration.
    """
    parser = argparse.ArgumentParser(
        description="jacoco-filter: Filter JaCoCo XML reports and adjust coverage counters."
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Optional path to .toml config file (default: jacoco_filter.toml)",
    )
    parser.add_argument(
        "--inputs",
        "-i",
        nargs="*",
        help="One or more glob patterns or directories to recursively collect input XML files "
        '(e.g. "target/**/jacoco.xml")',
    )
    parser.add_argument(
        "--exclude-paths",
        "-x",
        nargs="*",
        default=[],
        help='Optional glob patterns to exclude paths from processing (e.g. "**/test/**")',
    )
    parser.add_argument("--rules", "-r", type=Path, help="Path to the filter rules file")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose logging (DEBUG level)",
    )

    return parser.parse_args()


def evaluate_parsed_arguments(args: argparse.Namespace) -> dict:
    """
    Evaluates the parsed command-line arguments and merges them with the configuration file if provided.

    Parameters:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        dict: A dictionary containing the merged configuration.
    """
    if not args.inputs and not args.config:
        logger.error("Either --inputs or a valid --config file must be provided.")
        sys.exit(1)

    config = load_config(args.config) if args.config else {}
    logger.info("Config values: '%s'", str(config))

    # CLI has priority over config
    merged = {}

    # -----------
    # Inputs
    if args.inputs:
        merged["inputs"] = args.inputs
    else:
        merged["inputs"] = config.get("inputs", [])

    if not merged["inputs"]:
        logger.error("No input files provided. Use --inputs or define them in the config.")

    # -----------
    # Exclude paths
    if len(args.exclude_paths) > 0:
        merged["exclude_paths"] = args.exclude_paths
    else:
        merged["exclude_paths"] = config.get("exclude_paths", [])

    # -----------
    # Rules
    merged["rules"] = []

    if args.rules:
        # when rules are provided via CLI
        logger.info("   Loaded from file: %s", args.rules)
        merged["rules"] = load_filter_rules(args.rules)

    elif "rules" in config:
        # when rules are defined in the config
        logger.info("   Loaded inline_rules from config")
        for raw_line in config.get("rules", []):
            stripped = raw_line.strip()
            if stripped.startswith("#"):
                continue

            if not FilterRule.is_valid_line(stripped):
                if stripped:
                    logger.warning("Skipping invalid rule rule: '%s'", stripped)
                continue
            try:
                merged["rules"].append(FilterRule.parse(stripped))
            # pylint: disable=broad-except
            except Exception as e:
                logger.error("Failed to parse rule rule '%s': %s", stripped, e)

    if len(merged["rules"]) == 0:
        logger.error("No rules provided. Use --rules or define rules in the config.")

    # -----------
    # Verbose logging
    merged["verbose"] = args.verbose or config.get("verbose", False)

    # -----------
    logger.info("Final configuration:")
    logger.info("   inputs: %s", merged["inputs"])
    logger.info("   exclude_paths: %s", merged["exclude_paths"])
    logger.info("   rules: %s", merged["rules"])
    logger.info("   verbose logging: %s", merged["verbose"])

    return merged


def resolve_globs(patterns: Iterable[str], root_path: Path) -> list[Path]:
    """
    Resolves a list of glob patterns against a root path and returns a sorted list of file paths.

    Parameters:
        patterns (Iterable[str]): A list of glob patterns to match files.
        root_path (Path): The root directory to resolve the patterns against.
    Returns:
        list[Path]: A sorted list of resolved file paths.
    """
    files: set[Path] = set()

    for pattern in patterns:
        files.update(root_path.glob(pattern))

    return sorted(p.resolve() for p in files if p.is_file())


def apply_excludes(paths: list[Path], exclude_patterns: list[str], root_path: Path) -> list[Path]:
    """
    Applies exclusion patterns to a list of paths, returning only those that do not match any of the patterns.

    Parameters:
        paths (list[Path]): The list of paths to filter.
        exclude_patterns (list[str]): A list of glob patterns to exclude.
        root_path (Path): The root directory to resolve the paths against.
    Returns:
        list[Path]: A list of paths that do not match any of the exclusion patterns.
    """
    result = []
    for path in paths:
        try:
            relative = path.relative_to(root_path)
        except ValueError:
            # Path is outside root_path — optionally skip or keep
            continue

        if any(fnmatch.fnmatch(str(relative), pat) for pat in exclude_patterns):
            continue
        result.append(path)
    return result
