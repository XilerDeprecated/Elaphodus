"""
# Ultibar v1.2.3

The ultimate foo-bar experience, only one command away!

## Usage example:

Using ultibar is very easy, you can use it like this:
`ultibar run`
"""

from sys import argv

import utils.foobar as foobar
import utils.print.printer as printer


def main():
    """|no-doc|"""
    keyword, argument = None, None

    if len(argv) >= 2:
        keyword = argv[1]
    if len(argv) >= 3:
        argument = argv[2]

    if keyword == "run":
        printer.out(foobar.FooBar(int(argument) or 1)())
    else:
        printer.out("Unsupported command!")


if __name__ == "__main__":
    main()
