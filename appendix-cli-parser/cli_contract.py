"""A small CLI with a stable main(argv) -> int contract."""

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from typing import TextIO


class CliUsageError(ValueError):
    pass


class CourseArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliUsageError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = CourseArgumentParser(prog="notes")
    subparsers = parser.add_subparsers(dest="command", required=True)
    show = subparsers.add_parser("show", help="Show one UTF-8 note")
    show.add_argument("path", type=Path)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    try:
        args = build_parser().parse_args(argv)
    except CliUsageError as exc:
        print(f"usage error: {exc}", file=err)
        return 2

    try:
        text = args.path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"note not found: {args.path}", file=err)
        return 1
    except PermissionError:
        print(f"cannot read note: {args.path}", file=err)
        return 1

    print(text, end="" if text.endswith("\n") else "\n", file=out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
