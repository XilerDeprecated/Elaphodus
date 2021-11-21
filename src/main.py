# Copyright (c) 2021 Xiler Network
#  Full MIT License can be found in `LICENSE` at the project root.

"""The main script, so this is what does the hard work!"""
import re
from logging import basicConfig, DEBUG

from click import group, option

from src.utils.lexer import TokenTypes
from . import MultiCommand, Parser, Lexer


@group(cls=MultiCommand)
@option("-v", "--verbose", is_flag=True, help="Enable debug logging/verbose content")
def cli(verbose: bool):
    if verbose:
        basicConfig(level=DEBUG)


@cli.command(["generate", "gen"])
@option("-d", "--directory", "--dir", help="Override the directory that should be documented.")
@option("-m", "--match", help="Regex file matching statement. Defaults to supported file extensions.")
@option("-o", "--out", help="Set the output directory")
def generate(directory: str, match: str, out: str):
    """Generate the documentation"""
    directory = directory or "./"
    match = re.compile(match or ".(py)")

    parser = Parser(directory, match)
    lexer = Lexer(parser.parse())
    tokens = lexer.tokenize()


if __name__ == "__main__":
    cli()
