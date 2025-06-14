# jacoco_filter/main.py

from pathlib import Path
import sys
import traceback

from jacoco_filter.cli import parse_arguments
from jacoco_filter.parser import JacocoParser
from jacoco_filter.rules import load_filter_rules
from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.serializer import ReportSerializer


def main():
    try:
        args = parse_arguments()

        print("📥 Loading report...")
        parser = JacocoParser(args.input)
        report = parser.parse()

        print("📜 Loading filter rules...")
        rules = load_filter_rules(args.rules)
        for rule in rules:
            print(f"   ↳ {rule.scope}:{rule.pattern}")

        print("🧹 Applying filters...")
        engine = FilterEngine(rules)
        engine.apply(report)
        print(f"   ↳ Removed {engine.stats['classes_removed']} class(es), {engine.stats['methods_removed']} method(s)")

        print("🧮 Updating counters...")
        updater = CounterUpdater()
        updater.apply(report)

        print(f"💾 Saving output to {args.output}")
        serializer = ReportSerializer(report)
        serializer.write_to_file(args.output)

        print("✅ jacoco-filter finished successfully.")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
