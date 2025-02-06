import os
from lark import Token, Lark
import sys

SCORE_TYPES = ("int", "float", "double", "bool")
MINECRAFT_TYPES = ("bool", "short", "int", "float", "double", "long")
TYPES = ("entity", "nbt", "string") + SCORE_TYPES
SCOREBOARD_NAME = "40planet_num"
STORAGE_NAME = "40planet:value"
NAMESPACE = "__namespace__"
DIGITS = '0123456789'

INTERPRETE_THESE = ("operator", "call_function", "make_array", "make_nbt", "make_selector", "define_var")

BUILT_IN_FUNCTION = ("print", "random", "type", "get_score", "get_data", "set_score", "set_data", "round", "del", "append", "is_module", "len", "divide", "multiply") + TYPES

OPERATOR_ID = {
    "+":1,
    "-":2,
    "*":3,
    "/":4,
    "%":5,
    "==":6,
    "!=":7,
    ">=":8,
    ">":9,
    "<=":10,
    "<":11,
    "!":12,
    "member":13,
    # ".":14
}

CNAME = 'CNAME'
INT = 'INT'
ESCAPED_STRING = 'ESCAPED_STRING'
OPERATION = "operation"

NEW_LINE = "䗻"

lark_directory = os.path.join(os.path.dirname(__file__), "grammer.lark")
planet_parser = Lark.open(lark_directory)
  

#######################################
# ERRORS
#######################################

def error_as_txt(token, error_name, filename, details, line = ""):
    print(type(token))
    with open(filename, "r", encoding="utf-8") as file:
        line = file.read().split("\n")[token.line - 1]

    result = f'{error_name}: {details}\n'
    result += f'File {filename}, line {token.line}, col {token.column - 1}'
    result += "\n\n" + line
    if line[-1] != "\n": result += "\n"
    result += " " * (token.column - 1)
    result += "^" * (token.end_pos - token.start_pos)
    return result

#######################################
# VARIABLE
#######################################

class VariableComet:
    def __init__(self, name, temp = "", details = None) -> None:
        self.name = name
        self.temp = temp
        self.details = details

    def __repr__(self):
        return f"({self.name}, {self.temp})"

class Function:
    def __init__(self, name, type_, inputs, temp) -> None:
        self.name = name
        self.type = type_
        self.inputs = inputs
        self.temp = temp
    def __repr__(self) -> str:
        return f"name: {self.name}, temp: {self.temp}, inputs: {self.inputs}"
    
class CometToken:
    def __init__(self, type_, value, start_pos = None, line = None, column = None, end_line = None, end_column = None, end_pos = None, command = None):
        self.tok = Token(type_, value, start_pos, line, column, end_line, end_column, end_pos)
        self.command = command
        self.type = type_
        self.value = value
        self.start_pos = start_pos
        self.line = line
        self.column = column
        self.end_line = end_line
        self.end_column = end_column
        self.end_pos = end_pos

    def __repr__(self):
        return f"CometToken(type:{self.type}, value:{self.value}, command:{self.command})"

class CometClass:
    def __init__(self):
        self.method = []
        self.variables = []