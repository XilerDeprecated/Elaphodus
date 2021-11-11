# Copyright (c) 2021 Xiler Network
#  Full MIT License can be found in `LICENSE` at the project root.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


# TODO: Properly implement this

class Parser:
    """
    Detects all files, and properly parses them.

    With parsing we mean properly indexing, and lexing all files.
    """

    def __init__(self, root: str):
        self.root = root
        self.files: Dict[str, ...] = self.get_all_files()
        print(self.root, self.files)

    def get_all_files(self):
        return {"a": "Not valid return"}

    def walker(self):
        ...
