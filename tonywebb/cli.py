"""Unified CLI for the Tony Webb cricket collection indexing toolkit."""

import argparse

from . import (
    build_browser,
    clean_transcriptions,
    clubs,
    compare,
    consensus,
    evaluate,
    extract_matches,
    extract_stats,
    index_scorecards,
    index_stats,
    promote_reviewed,
    reconcile,
    transcribe,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tonywebb",
        description="Tony Webb minor counties collection indexing toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for module in (
        transcribe,
        clean_transcriptions,
        extract_matches,
        extract_stats,
        index_stats,
        index_scorecards,
        evaluate,
        consensus,
        promote_reviewed,
        reconcile,
        compare,
        build_browser,
        clubs,
    ):
        module.register_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
