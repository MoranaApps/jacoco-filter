"""
This module is the entry point for the jacoco-filter CLI application.
"""

import logging
from pathlib import Path
import sys
import traceback

from jacoco_filter.cli import parse_arguments, resolve_globs, apply_excludes, evaluate_parsed_arguments
from jacoco_filter.logging_config import setup_logging
from jacoco_filter.model import JacocoReport
from jacoco_filter.parser import JacocoParser
from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.serializer import ReportSerializer


def main():
    """
    Main entry point for the jacoco-filter application.

    Returns:
        None
    """
    try:
        parsed_args = parse_arguments()
        setup_logging(parsed_args.verbose)
        logger = logging.getLogger(__name__)

        args = evaluate_parsed_arguments(parsed_args)
        root_dir = Path.cwd()

        logger.info("jacoco-filter started")

        # 1. Resolve all input globs (find files)
        resolved_files = resolve_globs(args["inputs"], root_dir)

        # 2. Apply exclude patterns
        input_files = apply_excludes(resolved_files, args["exclude_paths"], root_dir)

        if not input_files:
            raise FileNotFoundError("No input files remain after exclusions.")

        logger.info("Loaded rules:")
        for rule in args["rules"]:
            logger.info("   %s:%s", rule.scope.value, rule.pattern)

        logger.info("Found %s input file(s) to process.", len(input_files))
        for file in input_files:
            logger.info(" - %s", file)

        for file in input_files:
            logger.info("Loading report '%s' ...", file)

            parser = JacocoParser(file)
            report: JacocoReport = parser.parse()

            logger.info("Applying filters...")
            engine = FilterEngine(args["rules"])
            engine.apply(report)
            logger.info(
                "Removed %s class(es), %s method(s)",
                engine.stats["classes_removed"],
                engine.stats["methods_removed"],
            )

            logger.info("Updating counters...")
            updater = CounterUpdater()
            updater.apply(report)

            # DEBUG
            for package in report.packages:
                for sourcefile in package.sourcefiles:
                    logger.debug("Source file '%s' counters: %s", sourcefile.name, sourcefile.counters)

            filtered_file = file.with_name(file.stem + ".filtered.xml")

            logger.info("Saving output to %s", filtered_file)
            serializer = ReportSerializer(report)
            serializer.write_to_file(filtered_file)

            logger.info("jacoco-filter finished successfully.")

    # pylint: disable=broad-except
    except Exception as e:
        logger.error("Error: %s", e)
        traceback.print_exc()
        sys.exit(1)
