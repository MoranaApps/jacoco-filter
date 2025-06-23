import argparse
import fnmatch
import logging
import sys

import tomli

from pathlib import Path
from typing import Iterable
from jacoco_filter.rules import FilterRule, load_filter_rules

logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}.")
        return {}

    with config_path.open("rb") as f:
        logger.info(f"Loading configuration from {config_path}...")
        return tomli.load(f)


def parse_arguments() -> dict:
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
        help='One or more glob patterns or directories to recursively collect input XML files (e.g. "target/**/jacoco.xml")',
    )
    parser.add_argument(
        "--exclude-paths",
        "-x",
        nargs="*",
        default=[],
        help='Optional glob patterns to exclude paths from processing (e.g. "**/test/**")',
    )
    parser.add_argument(
        "--rules", "-r", type=Path, help="Path to the filter rules file"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()

    # -----------
    # Enforce that at least one of --inputs or --config must be provided
    if not args.inputs and not args.config:
        logger.error("Either --inputs or a valid --config file must be provided.")
        sys.exit(1)

    config = load_config(args.config) if args.config else {}

    # CLI has priority over config
    merged = {}

    # -----------
    # Inputs
    if args.inputs:
        merged["inputs"] = args.inputs
    else:
        merged["inputs"] = config.get("inputs", [])

    if not merged["inputs"]:
        logger.error(
            "No input files provided. Use --inputs or define them in the config."
        )

    # -----------
    # Exclude paths
    if args.exclude_paths is not None:
        merged["exclude_paths"] = args.exclude_paths
    else:
        merged["exclude_paths"] = config.get("exclude_paths", [])

    # -----------
    # Rules
    merged["rules"]: list[FilterRule] = []

    if args.rules:
        # when rules are provided via CLI
        logger.info(f"   Loaded from file: {args.rules}")
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
                    logger.warning(f"Skipping invalid rule rule: '{stripped}'")
                continue
            try:
                merged["rules"].append(FilterRule.parse(stripped))
            except Exception as e:
                logger.error(f"Failed to parse rule rule '{stripped}': {e}")

    if len(merged["rules"]) == 0:
        logger.error("No rules provided. Use --rules or define rules in the config.")

    # -----------
    # Verbose logging
    if args.verbose:
        merged["verbose"] = True

    # -----------
    logger.info("Final configuration:")
    logger.info(f"   inputs: {merged['inputs']}")
    logger.info(f"   exclude_paths: {merged['exclude_paths']}")
    logger.info(f"   rules: {merged['rules']}")
    logger.info(f"   verbose logging: {merged['verbose']}")

    return merged


def resolve_globs(patterns: Iterable[str], root_path: Path) -> list[Path]:
    """
    Resolves glob patterns relative to the given root path.
    Returns a list of absolute Paths that are files.
    """
    files = set()

    for pattern in patterns:
        files.update(root_path.glob(pattern))

    return sorted(p.resolve() for p in files if p.is_file())


def apply_excludes(
    paths: list[Path], exclude_patterns: list[str], root_path: Path
) -> list[Path]:
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
