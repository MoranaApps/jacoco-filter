import argparse
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="jacoco-filter: Filter JaCoCo XML reports and adjust coverage counters."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        help="Path to the input jacoco.xml file"
    )
    parser.add_argument(
        "--rules", "-r",
        required=True,
        type=Path,
        help="Path to the filter rules file"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        type=Path,
        help="Path to the output XML file"
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"Input file not found: {args.input}")
    if not args.rules.exists():
        parser.error(f"Rules file not found: {args.rules}")
    if args.output.is_dir():
        parser.error("Output path must be a file, not a directory.")

    return args
