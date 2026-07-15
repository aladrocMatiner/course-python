"""Stable command-line adapter for the SQLite-backed service."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TextIO

from .domain import Order, OrderError
from .repositories import SQLiteOrderRepository
from .service import OrderService

LOGGER_NAME = "order_tracker"


def _quantity(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("QUANTITY must be an integer") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="order-tracker")
    parser.add_argument("--database", metavar="PATH")
    parser.add_argument("--verbose", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="create a pending order")
    add.add_argument("order_id", metavar="ORDER_ID")
    add.add_argument("item", metavar="ITEM")
    add.add_argument("quantity", metavar="QUANTITY", type=_quantity)

    advance = commands.add_parser("advance", help="advance one status")
    advance.add_argument("order_id", metavar="ORDER_ID")

    commands.add_parser("list", help="list orders by identifier")
    return parser


def _logger(verbose: bool, stderr: TextIO) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.INFO if verbose else logging.CRITICAL + 1)
    handler = logging.StreamHandler(stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def _order_json(order: Order, *, include_item: bool) -> str:
    data: dict[str, object] = {
        "order_id": order.order_id,
        "status": order.status,
    }
    if include_item:
        data.update(item=order.item, quantity=order.quantity)
    return json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _event(
    logger: logging.Logger,
    *,
    phase: str,
    outcome: str,
    order_id: str | None = None,
    category: str | None = None,
    count: int | None = None,
) -> None:
    fields = [f"event={phase}"]
    if order_id is not None:
        fields.append(f"order_id={order_id}")
    if count is not None:
        fields.append(f"count={count}")
    fields.append(f"outcome={outcome}")
    if category is not None:
        fields.append(f"category={category}")
    logger.info(" ".join(fields))


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    environment = os.environ if environ is None else environ
    output = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr
    args = build_parser().parse_args(argv)
    logger = _logger(args.verbose, errors)

    configured = args.database if args.database is not None else environment.get("ORDER_TRACKER_DB")
    if configured is None or not configured.strip():
        print("error: database path required; use --database PATH or ORDER_TRACKER_DB", file=errors)
        return 2

    phase = args.command
    order_id = getattr(args, "order_id", None)
    try:
        with OrderService(SQLiteOrderRepository(Path(configured))) as service:
            if args.command == "add":
                order = service.create(args.order_id, args.item, args.quantity)
                print(_order_json(order, include_item=False), file=output)
                _event(logger, phase=phase, order_id=order.order_id, outcome="success")
            elif args.command == "advance":
                order = service.advance(args.order_id)
                print(_order_json(order, include_item=False), file=output)
                _event(logger, phase=phase, order_id=order.order_id, outcome="success")
            else:
                orders = service.list_orders()
                for order in orders:
                    print(_order_json(order, include_item=True), file=output)
                _event(logger, phase=phase, count=len(orders), outcome="success")
        return 0
    except OrderError as exc:
        _event(
            logger,
            phase=phase,
            order_id=order_id,
            outcome="error",
            category=exc.code,
        )
        print(f"error[{exc.code}]: {exc}", file=errors)
        return 1


def run() -> int:
    """Console-script entry point."""

    return main()

