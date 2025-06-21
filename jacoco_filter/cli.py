import argparse
import fnmatch
from pathlib import Path
from typing import Iterable


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="jacoco-filter: Filter JaCoCo XML reports and adjust coverage counters."
    )
    parser.add_argument(
        "--inputs", "-i",
        required=True,
        nargs="+",
        help='One or more glob patterns or directories to recursively collect input XML files (e.g. "target/**/jacoco.xml")'
    )
    parser.add_argument(
        "--exclude-paths", "-x",
        nargs="*",
        default=[],
        help='Optional glob patterns to exclude paths from processing (e.g. "**/test/**")'
    )
    parser.add_argument(
        "--rules", "-r",
        required=True,
        type=Path,
        help="Path to the filter rules file"
    )

    args = parser.parse_args()

    if not args.rules.exists():
        parser.error(f"Rules file not found: {args.rules}")

    return args


def resolve_globs(patterns: Iterable[str], root_path: Path) -> list[Path]:
    """
    Resolves glob patterns relative to the given root path.
    Returns a list of absolute Paths that are files.
    """
    files = set()

    for pattern in patterns:
        files.update(root_path.glob(pattern))

    return sorted(p.resolve() for p in files if p.is_file())


def apply_excludes(paths: list[Path], exclude_patterns: list[str], root_path: Path) -> list[Path]:
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
