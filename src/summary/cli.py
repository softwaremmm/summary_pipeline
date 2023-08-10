"""Command Line Interface"""
import logging
import sys
from summary.cli_args import Arguments
from summary.summarise import summarise


def main():
    """CLI entry point."""
    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=logging.DEBUG,
    )

    cli_args = Arguments(sys.argv[1:])

    summarise(cli_args)
