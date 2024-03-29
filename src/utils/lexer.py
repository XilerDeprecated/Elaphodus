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
    DECORATOR = "DECORATOR"

    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"

    CHAR = 'CHARACTER-STRING'
    STRING = 'STRING'


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
    'class': TokenType(TokenTypes.CLASS, 'class', ':\n'),
    'def': TokenType(TokenTypes.FUNCTION, 'def', ':\n'),
    '@': TokenType(TokenTypes.DECORATOR, '@'),
    '\'': TokenType(TokenTypes.CHAR, '\'', '\''),
    '"': TokenType(TokenTypes.STRING, '"', '"'),
    'if': TokenType(TokenTypes.IF, 'if', ':'),
    'elif': TokenType(TokenTypes.ELIF, 'elif', ':'),
    'else': TokenType(TokenTypes.ELSE, 'else', ':')
}

multi_tokens = [token for token in start_tokens.keys() if len(token) > 1]


def remove_unique_start(tokens: List[str]) -> List[str]:
    chars = {token[0]: 0 for token in tokens}

    for token in tokens:
        chars[token[0]] += 1

    return [token for token in tokens if chars[token[0]] != 1]


collision_tokens = remove_unique_start(list(start_tokens.keys()))
collision_tokens = sorted(collision_tokens, key=len, reverse=True)


@dataclass
class Token:
    type: TokenType
    value: Union[str, Dict[str, Any]]

    def __post_init__(self):
        if cast := getattr(self, f"cast_to_{self.type.represents.value}".lower().replace('-', '_'), None):
            cast()

    def cast_to_function(self):  # sourcery no-metrics
        call: Optional[str] = None
        arguments: Dict[str, Optional[Dict[str, str]]] = {}
        return_type: Optional[str] = None

        curr_str = ""
        passed_function_token = False

        for char in self.value:
            curr_str += char

            if char == " " and not passed_function_token:
                curr_str = ""
                passed_function_token = True
            elif passed_function_token:
                current = curr_str.strip()[:-1]
                if char == "(":
                    call = current
                    curr_str = ""
                elif char in [",", ")"]:
                    argument_name: str = ""
                    arg_props: Dict[str, str] = {}

                    if (
                            (split_by_annotation := current.split(":"))
                            and len(split_by_annotation) == 2
                    ):
                        argument_name = split_by_annotation[0].strip()
                        arg_props["annotation"] = split_by_annotation[1].strip()

                    if (
                            (split_by_default := current.split("="))
                            and len(split_by_default) == 2
                    ):
                        if argument_name:
                            arg_props["annotation"] = arg_props["annotation"].split("=")[0].strip()
                        else:
                            argument_name = split_by_default[0].strip()
                        arg_props["default"] = split_by_default[1].strip()

                    if not argument_name:
                        argument_name = current.strip()

                    if argument_name:
                        arguments[argument_name] = arg_props
                    curr_str = ""
                elif curr_str.strip() == "->":
                    return_type = ""
                    curr_str = ""
                elif return_type is not None and char != ":":
                    return_type += char

        self.value = {
            "call": call,
            "arguments": arguments,
            "return_type": return_type
        }

    def cast_to_class(self):
        call = None
        parameters = {}
        has_passed_token = False

        curr_str = ""

        for char in self.value:
            if not has_passed_token \
                    and curr_str == "class" \
                    and char == " ":
                has_passed_token = True
                curr_str = ""
                continue
            elif has_passed_token:
                if char in ["(", ":"]:
                    if not parameters:
                        call = curr_str.strip()
                    curr_str = ""
                    continue
                elif char in [",", ")"]:
                    parameter_split = curr_str.split("=")

                    if len(parameter_split) == 2:
                        parameters[parameter_split[0].strip()] = parameter_split[1].strip()
                    else:
                        parameters[len(parameters)] = parameter_split[0].strip()
                    continue

            if char == ":":
                break

            curr_str += char

        self.value = {
            "call": call,
            "parameters": parameters
        }

    def cast_to_comment(self):
        self.value = self.value.strip()[1:].strip()

    def cast_to_multiline_comment(self):
        self.value = self.value.strip()[3:-3].strip()

    def cast_to_char(self):
        self.value = self.value.strip()[1:-1]

    def cast_to_string(self):
        self.cast_to_char()

    def cast_to_import(self):
        self.value = [v for v in self.value.split(" ") if v][1]

    def cast_to_from_import(self):
        curr_str = ""
        module: Optional[str] = None
        imports: List[str] = []

        started_location = False
        started_imports = False

        for char in self.value:
            if curr_str == "from" and char == " ":
                curr_str = ""
                started_location = True
            elif not module and \
                    started_location and \
                    not started_imports and \
                    char == " ":
                module = curr_str.strip()
                curr_str = ""
            elif curr_str == "import" and char == " ":
                curr_str = ""
                started_imports = True
            elif started_imports and char == ",":
                imports.append(curr_str.strip())
                curr_str = ""
            else:
                curr_str += char

        imports.append(curr_str.strip())

        self.value = {
            "module": module,
            "imports": imports
        }


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

                    has_collision = any(
                        col_token.startswith(curr_content + line[column + 1])
                        for col_token in collision_tokens
                    )

                    if not has_collision and curr_content in start_tokens:
                        curr_token_type = start_tokens[curr_content]
                elif char in start_tokens:
                    curr_content = char
                    curr_token_type = start_tokens[char]
                else:
                    curr_token_type = None
                    curr_content = None
                    curr_token = ""

        return tokens

    def __tokenize(self, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: self.__lex_content(value)
            for key, value in content.items()
        }

    def __lex_content(self, content: Union[str, Dict[str, Any]]) -> Union[List[Token], Dict[str, Any]]:
        if isinstance(content, str):
            return self.lex(content)

        return self.__tokenize(content)

    def tokenize(self):
        return self.__tokenize(self.parsed)
