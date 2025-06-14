from pathlib import Path

from jacoco_filter.cli import parse_arguments
from jacoco_filter.parser import JacocoParser

if __name__ == "__main__":
    args = parse_arguments()
    print("Parsed arguments:")
    print(f"  input:  {args.input}")
    print(f"  rules:  {args.rules}")
    print(f"  output: {args.output}")

    parser = JacocoParser(xml_path=args.input)
    report = parser.parse()

    print(f"Found {len(report.packages)} packages")


