from jacoco_filter.cli import parse_arguments

if __name__ == "__main__":
    args = parse_arguments()
    print("Parsed arguments:")
    print(f"  input:  {args.input}")
    print(f"  rules:  {args.rules}")
    print(f"  output: {args.output}")

