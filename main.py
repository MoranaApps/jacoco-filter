from pathlib import Path

from jacoco_filter.cli import parse_arguments
from jacoco_filter.counter_updater import CounterUpdater
from jacoco_filter.filter_engine import FilterEngine
from jacoco_filter.parser import JacocoParser
from jacoco_filter.rules import load_filter_rules
from jacoco_filter.serializer import ReportSerializer

if __name__ == "__main__":
    # Parse CLI arguments
    args = parse_arguments()
    print("Parsed arguments:")
    print(f"  input:  {args.input}")
    print(f"  rules:  {args.rules}")
    print(f"  output: {args.output}")

    # Parse JaCoCo XML report
    parser = JacocoParser(xml_path=args.input)
    report = parser.parse()
    print(f"✅ Parsed report with {len(report.packages)} package(s)")

    # Load filter rules
    rules = load_filter_rules(args.rules)
    print(f"✅ Loaded {len(rules)} rule(s):")
    for rule in rules:
        print(f"   - {rule.scope}:{rule.pattern}")

    # Apply filtering
    engine = FilterEngine(rules)
    engine.apply(report)

    print(f"✅ Filter applied: {engine.stats['classes_removed']} class(es) and {engine.stats['methods_removed']} method(s) removed.")

    updater = CounterUpdater()
    updater.apply(report)

    for pkg in report.packages:
        for cls in pkg.classes:
            for counter in cls.counters:
                print(f"[DEBUG] Class '{cls.name}' counter {counter.type}: missed={counter.missed}, covered={counter.covered}")

    print("✅ Counters updated successfully.")

    serializer = ReportSerializer(report)
    serializer.write_to_file(args.output)

    print(f"✅ Filtered report saved to: {args.output}")