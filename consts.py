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

def get_executable_path():
    dir_ = __file__.split("\\")
    del dir_[-1]
    dir_ = "\\".join(dir_)
    return dir_

python_file_path = get_executable_path()
lark_directory = python_file_path + "/grammer.lark"
planet_parser = Lark.open(lark_directory)

# 이스케이프 문자 처리하기(정규식에 쓰인 \d를 인식 못하는 듯)
# planet_parser = """%import common.CNAME
# //%import common.FLOAT
# FLOAT: /\d+\.\d+/
# //%import common.INT
# INT: /\d+/
# // %import common.ESCAPED_STRING
# ESCAPED_STRING: /"([^"\\]|\\.)*"/
#     | /'([^'\\]|\\.)*'/
#     // | /[a-zA-z]+/
# // %import common.WS_INLINE
# // %ignore WS_INLINE
# %import common.WS


# start: (statement eol)* statement?

# ?statement.-998: minecraft_command | command_macro
#     | eol
#     | condition
#     | function_def
#     | variable_def
#     | variable_set
#     | if_statement
#     | while_statement
#     | execute
#     | return_
#     | break_
#     | import_statement
#     // | class_def

# minecraft_command: /\/[^\$][^;\n]*/
# command_macro: "/$" ( macro_ | word )+
# // minecraft_command.10: "/" (macro | word)+ eol
# macro_: "$(" condition ")"
# word.-999: /[^;\n\$]+/

# // ?new_line: /\n/
# ?eol: /\n/ | ";"

# // 중괄호 블럭
# block: "{" statement* "}"
#     | statement

# parameter_list: _seperated{parameter, ","}
# ?parameter: "var" CNAME
# arguments: _seperated{argument, ","}
# argument: condition
#     | selector //-> selector


# // import문
# import_statement: "import" CNAME

# //함수 선언, 실행
# //--------------------------------------------------------------
# function_def: "def" CNAME "(" [parameter_list] ")" block
# function_call: CNAME "(" [arguments] ")"



# //변수 설정
# //--------------------------------------------------------------
# variable_def: "var" CNAME
# variable_set: CNAME set_value
#     | variable set_value
#     | variable_def set_value
# ?set_value : "=" condition

# //사칙연산
# //--------------------------------------------------------------

# // expression = 어떠한 값 (변수, 사칙연산 등)
# ?expression: expression "+" term    -> add
#         | expression "-" term       -> sub
#         | term

# ?term: term "*" factor  -> mul
#     | term "/" factor   -> div
#     | term "%" factor   -> mod
#     | factor

# ?factor: value
#     | "-" factor    -> neg
#     | "(" condition ")"

    
# //멤버연산
# //--------------------------------------------------------------
# member_operation: variable "[" expression "]"
#     | array "[" INT "]"
#     | array "[" /[+-]\d+/ "]"
# dot_operation: variable "." CNAME
#     | nbt "." CNAME

# //값 토큰 설정
# //--------------------------------------------------------------
# _seperated{x, sep}: (x (sep x)*)?

# ?variable.-1000: dot_operation
#     | member_operation
#     | CNAME
#     | pointer
#     | address
#     | function_call
#     // | method
# pointer: "*" "(" variable ")"
#     | "*" variable
# address: "&" "(" variable ")"
#     | "&" variable -> address

# array: "[" _seperated{condition, ","} "]"
# nbt: "{" _seperated{pair, ","} "}"
# ?pair: CNAME ":" condition

# ?number:/\d+[bdf]?/
#     | /\d+\.\d+[bdf]?/
#     | /\.\d+[bdf]?/
# ?value: ESCAPED_STRING
#     | variable
#     | FLOAT
#     | INT
#     | array
#     | nbt
#     | number


# //키워드 설정
# //--------------------------------------------------------------
# return_: "return" condition
# break_.10: "break"

# //조건문, 반복문 설정
# //--------------------------------------------------------------
# if_statement: "if" "(" condition ")" block ("else" block)?
# while_statement: "while" "(" condition ")" block


# //논리연산
# //--------------------------------------------------------------
# ?logic_operation : expression
#     | expression "==" expression    -> equal
#     | expression ">" expression     -> bigger
#     | expression ">=" expression    -> bigger_equal
#     | expression "<" expression     -> smaller
#     | expression "<=" expression    -> smaller_equal
#     | expression "!=" expression    -> not_equal
#     | "!" "(" logic_operation ")"   -> not
# ?condition: logic_operation
#     | condition "and" condition -> and
#     | condition "or" condition  -> or


# // execute 설정
# //--------------------------------------------------------------
# ?minecraft_number: /[+-]?(\d+(\.\d+)?|\.\d+)/
# ?minecraft_range: minecraft_number
#     | /[+-]?(\d+(\.\d+)?|\.\d+)\.\./
#     | /\.\.[+-]?(\d+(\.\d+)?|\.\d+)/
#     | /[+-]?(\d+(\.\d+)?|\.\d+)\.\.[+-]?(\d+(\.\d+)?|\.\d+)/
# ?minecraft_id: MINECRAFT_NAME ":" MINECRAFT_NAME
#     | MINECRAFT_NAME
# ?minecraft_id_tag: "#" minecraft_id
#     | minecraft_id
# MINECRAFT_NAME: /[a-zA-Z0-9_]+/
# ?json_pair: /"([^"\\]|\\.)*"/ ":" json_value
# ?json_value: /"([^"\\]|\\.)*"/ 
#     | number
#     | "true"
#     | "false"
#     | "{" _seperated{json_pair, ","} "}" -> json_

# ?selector: /@[parsen]/ ("[" _seperated{selector_parameter, ","} "]")?
# selector_parameter: /tag=/ (/!/? MINECRAFT_NAME)?
#     | /advancements=/ minecraft_id_tag
#     | /distance=/ minecraft_range
#     | /d[xyz]=/ INT
#     | /gamemode=/ /!?(?:adventure|creative|survival|spectator)/
#     | /level=/ minecraft_range
#     | /limit=/ INT
#     | /name=/ /!/? MINECRAFT_NAME
#     | "nbt=" /!/? nbt                                                -> nbt
#     | /predicate=/ minecraft_id
#     | "scores=" "{" (MINECRAFT_NAME "=" minecraft_range)? ("," MINECRAFT_NAME "=" minecraft_range)* "}" -> scores
#     | /sort=/ /(arbitrary|furthest|nearest|random)/
#     | /team=/ MINECRAFT_NAME
#     | /[xyz]=/ minecraft_number
#     | /[xy]_rotation=/ minecraft_range
#     | /type=/ /!/? minecraft_id_tag



# ?coordinate_set: coord coord coord
#     | /\^([+-]?(\d+(\.\d+)?|\.\d+))?/ /\^([+-]?(\d+(\.\d+)?|\.\d+))?/ /\^([+-]?(\d+(\.\d+)?|\.\d+))?/

# ?coord: /~([+-]?(\d+(\.\d+)?|\.\d+))?/
#     | minecraft_number

# execute: "execute" "(" execute_parameter+ ")" block
# execute_parameter: /as/ selector
#     | /if/ execute_if
#     | /unless/ execute_if
#     | /positioned/ execute_positioned
#     | /in/ minecraft_id_tag
#     | /align/ /(xyz|xzy|yxz|yzx|zxy|zyx|xy|yx|xz|zx|yz|zy|x|y|z)/
#     | /anchored/ /(eyes|feet)/
#     | /at/ selector
#     | /facing/ execute_facing
#     | /on/ /(attacker|controller|leasher|origin|owner|passengers|target|vehicle)/
#     | /rotated/ execute_rotated
#     | /store/ /(success|result)/ execute_store
#     | /summon/ minecraft_id

# ?execute_positioned: coordinate_set
#     | /over/ /(motion_blocking|motion_blocking_no_leaves|ocean_floor|world_surface)/
#     | /as/ selector
# ?execute_rotated: coord coord
#     | /as/ selector

# ?execute_facing: coordinate_set
#     | /entity/ selector

# ?nbt_dir: MINECRAFT_NAME
#     | ESCAPED_STRING
#     | nbt_dir /\[\d+\]/
#     | nbt_dir /\./ (MINECRAFT_NAME | ESCAPED_STRING)
# ?execute_store: execute_store_list nbt_dir /(byte|double|float|int|long|short)/ minecraft_number
# ?execute_store_list: block_entity
#     | /bossbar/ minecraft_id
#     | /score/ (selector|MINECRAFT_NAME) MINECRAFT_NAME
#     | /storage/ minecraft_id

# ?execute_if: /predicate/ execute_if_predicate
#     | /boime/ coordinate_set minecraft_id_tag
#     | /block/ coordinate_set minecraft_id_tag
#     | /blocks/ coordinate_set coordinate_set coordinate_set /(all|masked)/
#     | /data/ execute_if_data nbt_dir
#     | /dimension/ minecraft_id_tag
#     | /entity/ selector
#     | /function/ execute_if_function
#     | /items/ block_entity item_slot item
#     | /loaded/ coordinate_set
#     | /score/ scoreboard execute_if_score
# ?execute_if_predicate: "{" _seperated{json_pair, ","} "}"
#     | minecraft_id
# ?execute_if_data: block_entity
#     | /storage/ minecraft_id
# execute_if_function: minecraft_id_tag
#     | if_function_block
# if_function_block: "{" statement* "}"
# ?block_entity: /block/ coordinate_set
#     | /entity/ selector
# ?item_slot: /(container|enderchest|horse|hotbar|inventory|player\.crafting|villager)\.(\d+|\*)/
#     | /contents/
#     | /weapon\.(?:\*|mainhand|offhand)/
#     | /horse\.(?:chest|saddle)/
#     | /armor\.(?:\*|body|chest|feet|head|legs)/
#     | /player.cursor/
# item: (/\*/ | minecraft_id_tag) /\[.*\]/?
# ?execute_if_score: /matches/ minecraft_range
#     | /(>=|<=|>|=|<)/ scoreboard
# ?scoreboard: (selector|ESCAPED_STRING|MINECRAFT_NAME) (ESCAPED_STRING|MINECRAFT_NAME)



# // TODO : class 설정
# //--------------------------------------------------------------
# // class_def: "class" CNAME "{" ((function_def | variable_def) eol?)* "}"
# // method: variable "." CNAME "(" [arguments] ")"



# %ignore WS
# %ignore /#[^\n;]*/       // 주석
# %ignore /\n/"""
  

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
        return f"CometToken(type:{self.type}, value:{self.value})"

class CometClass:
    def __init__(self):
        self.method = []
        self.variables = []