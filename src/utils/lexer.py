# Copyright (c) 2021 Xiler Network
#  Full MIT License can be found in `LICENSE` at the project root.
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional, Union


class TokenTypes(Enum):
    COMMENT = "COMMENT"
    MULTILINE_COMMENT = "MULTILINE-COMMENT"

    IMPORT = "IMPORT"
    FROM_IMPORT = "FROM-IMPORT"

    CLASS = "CLASS"
    FUNCTION = "FUNCTION"

    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"


@dataclass()
class TokenType:
    represents: TokenTypes

    start: str
    end: str = '\n'

    def __repr__(self):
        return self.represents.value


start_tokens = {
    '#': TokenType(TokenTypes.COMMENT, '#'),
    '"""': TokenType(TokenTypes.MULTILINE_COMMENT, '"""', '"""'),
    'import': TokenType(TokenTypes.IMPORT, 'import'),
    'from': TokenType(TokenTypes.FROM_IMPORT, 'from'),
    'class': TokenType(TokenTypes.CLASS, 'class', ':'),
    'def': TokenType(TokenTypes.FUNCTION, 'def', ':'),
    'if': TokenType(TokenTypes.IF, 'if', ':'),
    'elif': TokenType(TokenTypes.ELIF, 'elif', ':'),
    'else': TokenType(TokenTypes.ELSE, 'else', ':')
}

multi_tokens = [token for token in start_tokens.keys() if len(token) > 1]


@dataclass
class Token:
    type: TokenType
    value: str


class Lexer:
    def __init__(self, parsed: Dict[str, Any]):
        self.parsed = parsed

    @staticmethod
    def is_multichar_token(char: str, curr_content: Optional[str]):
        content_length = len(curr_content or [])

        return any(map(
            lambda token: len(token) > content_length and token[content_length] == char,
            multi_tokens
        ))

    def lex(self, content: str) -> List[Token]:
        tokens: List[Token] = []

        curr_token_type: Optional[TokenType] = None
        curr_content: Optional[str] = None
        curr_token: Optional[str] = ""

        for row, line in enumerate(content.replace('\r', '').split('\n')):
            line += '\n'

            for column, char in enumerate(line):
                # Currently getting value of token
                if curr_token_type:
                    curr_content += char

                    if char in curr_token_type.end:
                        curr_token += char
                    elif curr_token:
                        curr_token = ""

                    if curr_token_type.end in (char, curr_token):
                        tokens.append(Token(curr_token_type, curr_content.strip()))
                        curr_content = None
                        curr_token_type = None
                # Handle multi-char tokens
                elif self.is_multichar_token(char, curr_content):
                    if curr_content:
                        curr_content += char
                    else:
                        curr_content = char

                    if curr_content in start_tokens:
                        curr_token_type = start_tokens[curr_content or char]
                # Handle single-char tokens
                elif char in start_tokens:
                    curr_content = char
                    curr_token_type = start_tokens[char]
                else:
                    curr_token_type = None
                    curr_content = None
                    curr_token = ""

        return tokens

    def __lex_content(self, content: Union[str, Dict[str, Any]]) -> Union[List[Token], Dict[str, Any]]:
        if isinstance(content, str):
            return self.lex(content)
        else:
            return {
                key: self.__lex_content(value)
                for key, value in content.items()
            }

    def tokenize(self):
        return {
            key: self.__lex_content(value)
            for key, value in self.parsed.items()
        }
