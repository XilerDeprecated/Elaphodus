"""
# Ultibar v1.2.3

The ultimate foo-bar experience, only one command away!

## Usage example:

Using ultibar is very easy, you can use it like this:
`ultibar run`
"""

from sys import argv


def main():
    """|no-doc|"""
    if argv == "run":
        ...

    print("Unsupported command!")


if __name__ == "__main__":
    main()
