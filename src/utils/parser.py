# Copyright (c) 2021 Xiler Network
#  Full MIT License can be found in `LICENSE` at the project root.
import os
import re
from typing import TYPE_CHECKING, Pattern, Tuple, Set, Generator, Any

if TYPE_CHECKING:
    from typing import Dict


# TODO: Properly implement this

class Parser:
    """
    Detects all files, and properly parses them.

    With parsing we mean properly indexing, and lexing all files.
    """

    def __init__(self, root: str, pattern: Pattern[str]):
        self.root = root
        self.pattern = pattern

        ignore = ("__pycache__",)
        self.ignore: Pattern[str] = re.compile(fr"^(?!.*{'|'.join(ignore)}).*$")
        self.files: Dict[str, ...] = self.get_all_files()
        print(self.files)

    def get_all_files(self):
        return_dict: Dict[str, Set[str]] = dict(self.walk())

        # TODO: read file content

        return return_dict

    def walk(self) -> Generator[Tuple[str, Set[str]], Any, None]:
        for root, subdirs, files in os.walk(self.root):
            if not self.ignore.search(root):
                continue

            files = set(filter(
                self.pattern.search,
                filter(self.ignore.search, files)
            ))
            root = os.path.relpath(root, self.root)

            yield root, files
