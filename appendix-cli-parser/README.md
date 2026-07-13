# Appendix A · Building CLI Tools with the Standard Library

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll design a console command inspired by real tools: it will accept subcommands, required options, and show automatic help. We’ll use `argparse`, `pathlib`, and `logging` so you can ship professional scripts without external dependencies.

## Learning path
1. **Reminder**: `sys.argv` and its limitations.
2. **Basic `argparse` structure**: description, positional and optional args.
3. **Subcommands (`add_subparsers`)**: multiple actions in one tool.
4. **Richer output**: formatting, exit codes, logging.
5. **Basic packaging**: entry point with `if __name__ == "__main__"`.
6. **Light testing**: `argparse` + `pytest` with `capsys`.

## Learning objectives
- Configure an `ArgumentParser` with required and optional arguments.
- Implement subcommands to group functionality.
- Read/write files with `Path` based on user arguments.
- Log messages and return appropriate exit codes.
- Test commands by simulating argv.

## Why it matters
Even though there are stronger frameworks, mastering the standard library avoids dependencies and lets you build internal tools, deploy scripts, and data utilities quickly.

### Mini adventure
A CLI is like a remote control for your program: instead of clicking, you type short commands. If the remote is well designed (help + clear options), anyone can use it without fear.

## Prerequisites
- Functions, files, exceptions, modules, logging, and basic pytest fixtures.
- A disposable local directory; command tests should use `tmp_path` rather than real user files.

---

## 1. Basic `argparse`

```python illustrative
# cli.py
import argparse

parser = argparse.ArgumentParser(description="Notes manager")
parser.add_argument("title", help="Note file name")
parser.add_argument("--message", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.title, args.message, args.tags)
```

- `nargs="*"` allows multiple tags.
- `parser.parse_args()` already validates and generates help.

### Generated help
```text illustrative
python cli.py --help
```
It prints description, arguments, and usage automatically.

---

## 2. Subcommands

```python illustrative
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add", help="Add task")
add_parser.add_argument("text")

list_parser = subparsers.add_parser("list", help="List tasks")

args = parser.parse_args()
file_path = Path("todos.txt")

if args.command == "add":
    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(args.text + "\n")
elif args.command == "list":
    if file_path.exists():
        print(file_path.read_text(encoding="utf-8"))
    else:
        print("No tasks yet.")
```

- `dest="command"` tells you which subcommand was used.
- To append, use `file_path.open("a", encoding="utf-8")` as shown above. `Path.write_text()` replaces the file and does not accept an `append=True` argument.

---

## 3. Logging and exit codes

```python runnable
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    # logic
    logging.info("Note saved")
except Exception as exc:
    logging.error("Failure: %s", exc)
    sys.exit(1)
```

- `sys.exit(0)` means success; any non‑zero code means error.

---

## 4. Good practices
- Keep logic in functions for testing and reuse.
- Use `Path` for paths; don’t concatenate strings.
- Add examples in `ArgumentParser(description=...)` and `epilog`.

### Recommended structure
```python illustrative
def build_parser():
    parser = argparse.ArgumentParser(...)
    # configure
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # logic

if __name__ == "__main__":
    main()
```

- Lets you pass custom `argv` during tests.

### Simulate `argv` in a test
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

Use pytest's `tmp_path` for command files and `caplog` for log records. `capsys` is for text written to `stdout`/`stderr`.

---

## Guided exercises (with TODOs)
1. **A-1 · Expenses CLI**
   ```python todo
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```
   *Hint*: `Path("expenses.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Configurable logger**
   ```python todo
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
   ```
   *Hint*: `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## Common mistakes
- Forgetting `dest` or `required=True` for subparsers ⇒ the tool doesn’t know what to run.
- Not wrapping logic in `try/except` ⇒ raw tracebacks for expected errors.
- Using `print` for everything instead of logging ⇒ hard to filter.
- Not testing `argparse` with simulated arguments.

---

## Explained solutions
1. **Expenses CLI**: `subparsers.add_parser("add")` and `"report"`; write rows into `expenses.csv`. `report` reads and sums values.
2. **Configurable logger**: `parser.add_argument("--debug", action="store_true")`; when enabled, increase logger level and show detailed messages. Assert log records with pytest's `caplog`; reserve `capsys.readouterr()` for `print` output.

---

## Summary
With `argparse`, `logging`, and `pathlib` you can create robust, self‑documenting console tools that are easy to test — without external frameworks.

## Checkpoint and rubric
- **Correctness**: required options, subcommands, and exit codes match the command contract.
- **Readability**: help text and command names explain their purpose.
- **Error handling**: missing files and invalid arguments produce friendly, testable outcomes.
- **Verification**: simulate `argv`, use `tmp_path`, and assert logs with `caplog`.
- **Explanation**: distinguish parser behavior, domain logic, and terminal presentation.

## Closing reflection
When you master CLIs with the standard library, you gain autonomy to automate tasks and build professional utilities your teammates can run without installing anything else. These patterns show up again in deploy scripts and DevOps tools.
