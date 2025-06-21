# jacoco_filter/main.py

from pathlib import Path
import sys
import traceback

from jacoco_filter.cli import parse_arguments, resolve_globs, apply_excludes
from jacoco_filter.model import JacocoReport
from jacoco_filter.parser import JacocoParser
from jacoco_filter.rules import load_filter_rules
from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.serializer import ReportSerializer


def main():
    try:
        print("✅ jacoco-filter started")

        args = parse_arguments()
        root_dir = Path.cwd()
        print(f"Args: {args}")

        # 1. Resolve all input globs (find files)
        resolved_files = resolve_globs(args.inputs, root_dir)

        # 2. Apply exclude patterns
        input_files = apply_excludes(resolved_files, args.exclude_paths, root_dir)

        if not input_files:
            raise FileNotFoundError("No input files remain after exclusions.")

        print("📜 Loading filter rules...")
        rules = load_filter_rules(args.rules)
        for rule in rules:
            print(f"   ↳ {rule.scope}:{rule.pattern}")

        for file in input_files:
            print(f"📥 Loading report '{file}' ...")

            parser = JacocoParser(file)
            report: JacocoReport = parser.parse()

            print("🧹 Applying filters...")
            engine = FilterEngine(rules)
            engine.apply(report)
            print(f"   ↳ Removed {engine.stats['classes_removed']} class(es), {engine.stats['methods_removed']} method(s)")

            print("🧮 Updating counters...")
            updater = CounterUpdater()
            updater.apply(report)

            filtered_file = file.with_name(file.stem + ".filtered.xml")

            print(f"💾 Saving output to {filtered_file}")
            serializer = ReportSerializer(report)
            serializer.write_to_file(filtered_file)

            print("✅ jacoco-filter finished successfully.")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
