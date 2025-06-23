# jacoco_filter/main.py
import logging
from pathlib import Path
import sys
import traceback

from jacoco_filter.cli import parse_arguments, resolve_globs, apply_excludes
from jacoco_filter.logging_config import setup_logging
from jacoco_filter.model import JacocoReport
from jacoco_filter.parser import JacocoParser
from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.serializer import ReportSerializer

logger = logging.getLogger(__name__)


def main():
    try:

        args = parse_arguments()
        setup_logging(args["verbose"])
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
            logger.info(f"   {rule.scope.value}:{rule.pattern}")

        logger.info(f"Found {len(input_files)} input file(s) to process.")
        for file in input_files:
            logger.info(f" - {file}")

        for file in input_files:
            logger.info(f"Loading report '{file}' ...")

            parser = JacocoParser(file)
            report: JacocoReport = parser.parse()

            logger.info("Applying filters...")
            engine = FilterEngine(args["rules"])
            engine.apply(report)
            logger.info(
                f"Removed {engine.stats['classes_removed']} class(es), {engine.stats['methods_removed']} method(s)"
            )

            logger.info("Updating counters...")
            updater = CounterUpdater()
            updater.apply(report)

            filtered_file = file.with_name(file.stem + ".filtered.xml")

            logger.info(f"Saving output to {filtered_file}")
            serializer = ReportSerializer(report)
            serializer.write_to_file(filtered_file)

            logger.info("jacoco-filter finished successfully.")

    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)
