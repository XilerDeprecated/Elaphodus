# Copyright (c) 2021 Xiler Network
#  Full MIT License can be found in `LICENSE` at the project root
from __future__ import annotations

from pprint import pprint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Union, List, Any
    from .lexer import Token


class Transpiler:
    def __init__(self, tokens: Dict[str, Union[List[Token], Any]]):
        self.tokens = tokens

    @staticmethod
    def __transpile_token(token: Token) -> str:
        # TODO: Proper transpilation to markdown
        return str(token.value)

    def __transpile(self, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: self.__transpile_file(value)
            for key, value in content.items()
        }

    def __transpile_file(self, tokens: Union[List[Token], Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        if isinstance(tokens, list):
            return "\n".join(map(self.__transpile_token, tokens))

        return self.__transpile(tokens)

    def transpile(self) -> Dict[str, Union[str, Any]]:
        return self.__transpile(self.tokens)
