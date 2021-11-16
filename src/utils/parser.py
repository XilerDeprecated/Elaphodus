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
        return_dict: Dict[str, Any] = {}

        def read_file(path: str):
            with open(path, "r") as f:
                return f.read()

        for root, files in self.walk():
            path_keys = root.split(os.sep)

            loc = return_dict
            for key in path_keys:
                if key == ".":
                    for file in files:
                        loc[file] = read_file(os.path.join(self.root, file))
                    continue

                if key not in loc:
                    loc[key] = {}
                loc = loc[key]

                if key != path_keys[-1]:
                    continue

                for file in files:
                    loc.update({
                        file: read_file(os.path.join(self.root, root, file))
                    })

        return return_dict

    def walk(self) -> Generator[Tuple[str, Set[str]], Any, None]:
        for root, _, files in os.walk(self.root):
            if not self.ignore.search(root):
                continue

            files = set(filter(
                self.pattern.search,
                filter(self.ignore.search, files)
            ))
            root = os.path.relpath(root, self.root)

            yield root, files
