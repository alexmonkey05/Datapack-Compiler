
import tokenize
from anytree import Node, RenderTree
import os
import string
import shutil
import json
import re

# 정규식 패턴 정의
PATTERN = r'^(?:\-*[0-9]*\.{0,2}|\.\.\-*[0-9]*|\-*[0-9]*\.\.\-*[0-9]*|\-*[0-9]*|\.{0,2})$'

def is_score_range(input_string):
    # 정규식 패턴에 맞는지 검사
    return re.match(PATTERN, input_string) is not None


import sys
sys.setrecursionlimit(10**7)


#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
MINECRAFT_SELECTOR = "parsen"

MINECRAFTCOMMAND = "/"
TERM = ("*", "/", "%")
FACTOR = ("+", "-")
BASIC_OPERATOR = FACTOR + TERM + ("=", "==", "!=", ">", "<", ">=", "<=", ".")
LOGIC_OPERATOR = ("==", "!=", "!", ">", ">=", "<", "<=")
SCORE_TYPES = ("int", "float", "double", "bool")
TYPES = ("entity", "nbt", "string") + SCORE_TYPES
MEANS_END = (";", "]", "}")
SCOREBOARD_NAME = "40planet_num"
STORAGE_NAME = "40planet:value"
NAMESPACE = "__namespace__"

KEYWORDS = ( "if", "else", "while", "from", "import", "def", "break", "and", "or", "return", "execute", "var")#, "const" )

OPERATOR_TO_STRING = {
    "=":"equal",
    "+":"basic",
    "-":"basic",
    "*":"basic",
    "/":"basic",
    "%":"basic",
    "return": "return",
    "==": "basic",
    "!=": "basic",
    ">=": "basic",
    "<=": "basic",
    "<": "basic",
    ">": "basic",
    ".":"dot",
    "[":"big_paren",
    "(":"small_paren",
    "{":"nbt",
    "@": "entity",
    "and": "and_or",
    "or": "and_or",
    "member":"member",
    "!":"not",
    "dot": "dot"
}

OPERATOR_PRIORITY = {
    "=":0,
    "return": 0,
    "and":2,
    "or":2,
    "!":2,
    "==":3,
    "!=":3,
    ">":3,
    "<":3,
    ">=":3,
    "<=":3,
    "+":4,
    "-":4,
    "*":5,
    "/":5,
    "%":5,
    "dot":6,
    "member":6,
    "paren":100
}

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

INTERPRETE_THESE = ("operator", "call_function", "make_array", "make_nbt", "make_selector", "define_var")

BUILT_IN_FUNCTION = ("print", "random", "type", "get_score", "get_data", "set_score", "set_data", "round", "del", "append", "is_module", "len", "devide", "multiply") + TYPES

EXECUTE_KEYWORDS = ( "as", "at", "if", "positioned" )

MINECRAFT_TYPES = ("bool", "short", "int", "float", "double", "long")
#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, token, error_name, filename, details):
        self.token = token
        self.error_name = error_name
        self.details = details
        self.filename = filename

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        try:
            result += f'File {self.filename}, line {self.token.start[0]}, col {self.token.start[1]}'
            result += "\n\n" + self.token.line
            if self.token.line[-1] != "\n": result += "\n"
            result += " " * self.token.start[1]
            result += "^" * (self.token.end[1] - self.token.start[1])
        except:
            pass
        return result

class InvalidSyntaxError(Error):
    def __init__(self, token, filename, details=''):
        super().__init__(token, 'Invalid Syntax', filename, details)

#######################################
# PARSER
#######################################

class Parser:
    def __init__(self, tokens, filename):
        self.tokens = tokens
        self.filename = filename
        self.tok_idx = -1
        self.advance()
        self.variables = {
            "false":[Variable("false","bool",True,"false")],
            "true":[Variable("true","bool",True,"true")]
        }
        self.functions = {}

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):

        root = Node("root", token = "")

        while self.current_tok.type != 0:
            node, error = self.build_ast(root)
            if error: return root, error

            self.advance()

        return root, None
    def build_ast(self, parent): # 현재 토큰을 ast로 변환하여 parent 노드에 자식으로 추가시켜라
        if self.current_tok.type == 64: return Node("comment", token=self.current_tok), None
        elif self.current_tok.type == 5: return Node("indent", token=self.current_tok), None
        method_name = f'type_{self.current_tok.type}'
        method = getattr(self, method_name)
        node, error = method(parent)
        if error: return node, error
        if node.name != "new_line": node.parent = parent
        return node, None

    def is_next_paren(self):
        next_tok = self.advance()
        self.reverse()
        return next_tok.string == "("
    def type_1(self, parent): # NAME type
        if len(parent.children) > 0 and parent.children[0].name == "dot":
            tok = self.advance()
            self.reverse()
            if tok.string == "(":
                return self.make_tree_of_call_function()
            else: return Node(self.current_tok.string, token = self.current_tok), None
        elif self.current_tok.string in KEYWORDS:
            error = None
            if self.current_tok.string == "var":
                return self.define_var()
            elif self.current_tok.string == "const":
                return self.define_const()
            else:
                method_name = f'make_tree_of_{self.current_tok.string}'
                method = getattr(self, method_name)
                return method(parent)
        elif self.current_tok.string not in self.variables and self.current_tok.string not in self.functions and self.current_tok.string not in BUILT_IN_FUNCTION:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} was not defined"
            )
        elif self.is_next_paren():
            if self.current_tok.string in self.functions or self.current_tok.string in BUILT_IN_FUNCTION:
                return self.make_tree_of_call_function()
            else:
                return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} is not a function"
            )
        elif self.current_tok.string in self.variables:
            node = Node(self.current_tok.string, token = self.current_tok)
            tok = self.advance()
            if tok.string == "[":
                node.parent = parent
                return self.operator_member(parent)
            self.reverse()
            return node, None
        else:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} was unexpected"
            )
    def type_2(self, parent): # NUMBER type
        num = self.current_tok.string
        next_tok = self.advance()
        if next_tok.string == "b":
            num += "b"
        else:
            self.reverse()
        return Node(num, token = self.current_tok), None
    def type_3(self, parent): # STRING type
        return Node(self.current_tok.string, token = self.current_tok), None
    def type_4(self, parent): # NEWLINE type (end of the line)
        return Node("new_line", token = self.current_tok), None
    def type_6(self, parent):
        return self.type_4(parent)
    def type_55(self, parent): # OPERATOR type
        operator = self.current_tok.string
        if operator in MEANS_END: return self.type_4(parent)
        elif operator in BASIC_OPERATOR:
            pre_token = self.reverse()
            self.advance()
            if (operator != MINECRAFTCOMMAND or pre_token.string != "\n") and self.tok_idx > 1:
                node, error = self.operator_basic(parent)
                if error: return None, error
                return node, error
            else:
                node, error = self.minecraft_command()
                if error: return None, error
                return node, error
        elif self.current_tok.string in OPERATOR_TO_STRING:
            method_name = f'operator_{OPERATOR_TO_STRING[self.current_tok.string]}'
            method = getattr(self, method_name)
            node, error = method(parent)
            if error: return None, error
            return node, error
        else:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} was not defined operator"
            )
    def type_65(self, parent): # NEWLINE type (\n)
        return self.type_4(parent)

    def make_tree_of_if(self, parent, is_while = False):
        node = Node("if", token = self.current_tok)
        if is_while: node = Node("while", token = self.current_tok)
        condition_node = Node("condition", parent=node, token = "")
        error = self.is_next_match("(")
        if error: return None, error

        self.advance()
        while self.current_tok.string != ")":
            temp, error = self.build_ast(condition_node)
            if error: return None, error
            self.advance()
        self.advance()
        while self.current_tok.string == "\n" or self.current_tok.type == 4 and self.current_tok.type != 0: self.advance()
        assign_node, error = self.make_tree_of_assign(node)
        if error: return None, error
        assign_node.parent = node
        next_tok = self.advance()
        while next_tok.string == "\n" or next_tok.string == "" and next_tok.type != 0: next_tok = self.advance()
        if next_tok.string == "else":
            node.parent = parent
            else_tree, error = self.make_tree_of_else(parent)
            if error: return None, error
        else: self.reverse()
        return node, None
    def make_tree_of_else(self, parent):
        if len(parent.children) == 0: return None, InvalidSyntaxError(
            self.current_tok,
            self.filename,
            "\"else\" must be located behind \"if\""
        )
        if_node = parent.children[-1]
        if if_node.name != "if": return None, InvalidSyntaxError(
            self.current_tok,
            self.filename,
            "\"else\" must be located behind \"if\""
        )
        self.advance()
        while self.current_tok.string == "\n" or self.current_tok.type == 4 and self.current_tok.type != 0: self.advance()
        assign_node, error = self.make_tree_of_assign()
        if error: return None, error
        assign_node.parent = if_node
        return if_node, None
    def make_tree_of_while(self, parent):
        return self.make_tree_of_if(parent, True)
    def make_tree_of_import(self, parent):
        node = Node("import", token = self.current_tok)
        tok = self.advance()
        Node(tok.string, parent=node, token = self.current_tok)
        self.variables[tok.string] = Variable(tok.string, "module", False)
        return node, None
    def make_tree_of_def(self, parent):
        node = Node("define_function", token = self.current_tok)
        tok = self.advance()
        name = None
        type_ = "void"
        if tok.string in TYPES or tok.string == "void":
            type_ = tok.string
            Node(type_, parent=node, token = self.current_tok)
            tok = self.advance()
            name = tok.string
            Node(name, parent=node, token = self.current_tok)
        else:
            name = tok.string
            Node(type_, parent=node, token = "")
            Node(name, parent=node, token = self.current_tok)
        self.functions[name] = {"type": type_, "inputs":[]}

        error = self.is_next_match("(")
        if error: return None, error

        self.advance()
        input_node = Node("input", parent=node, token = None)
        while self.current_tok.string != ")":
            if self.current_tok.string == ",": self.advance()
            temp, error = self.define_var()
            temp.parent = input_node
            self.functions[name]["inputs"].append(temp.children[0])
            if error: return None, error
            self.advance()

        error = self.is_next_match("{")
        if error: return None, error
        self.advance()

        assign_node = Node("assign", parent=node, token = None)
        while self.current_tok.string != "}":
            temp, error = self.build_ast(assign_node)
            if error: return None, error
            self.advance()
        return node, None
    def make_tree_of_call_function(self):
        node = Node("call_function", token = None)
        Node(self.current_tok.string, parent=node, token = self.current_tok)
        error = self.is_next_match("(")
        if error: return None, error

        self.advance()
        input_cnt = 0
        input_node = Node("input", parent=node, token = None)
        while self.current_tok.string != ")":
            input_cnt += 1
            temp_node = Node(str(input_cnt), parent=input_node, token = self.current_tok)
            if self.current_tok.string == ",": self.advance()
            while self.current_tok.string != "," and self.current_tok.string != ")":
                temp, error = self.build_ast(temp_node)
                if error: return None, error
                self.advance()
        return node, None
    def make_tree_of_assign(self, parent = None):
        node = Node("assign", token = None, parent=parent)

        if self.current_tok.string != "{":
            while True:
                temp, error = self.build_ast(node)
                if error: return None, error
                elif temp.name == 'new_line' or (len(temp.children) > 0 and temp.children[-1].name == "assign"):
                    break
                self.advance()
            return node, None
        else:
            self.advance()
            while self.current_tok.string != "}":
                temp, error = self.build_ast(node)
                if error: return None, error
                self.advance()

        return node, None
    def make_tree_of_break(self, parent):
        return Node("break", token = self.current_tok), None
    def make_tree_of_and(self, parent):
        return self.operator_basic(parent)
    def make_tree_of_or(self, parent):
        return self.operator_basic(parent)
    def make_tree_of_return(self, parent):
        node = Node("operator", token = None)
        Node("return", token = None, parent=node)
        self.advance()
        temp, error = self.build_ast(node)
        if error: return None, error
        return node, None
    def make_tree_of_execute(self, parent):
        execute_node = Node("execute", token = self.current_tok)
        node = Node("condition", token = None, parent=execute_node)
        error = self.is_next_match("(")
        if error: return None, error
        paren_cnt = 1
        while paren_cnt > 0:
            tok = self.advance()
            if self.current_tok.string == "(": paren_cnt += 1
            elif self.current_tok.string == ")": paren_cnt -= 1
            else:
                temp_node = Node(tok.string, parent=node, token = tok)
                if tok.string == "function":
                    if self.advance().string == "{":
                        assign_node, error = self.make_tree_of_assign(temp_node)
                        if error: return error
                    else: self.reverse()
        error = self.is_next_match("{")
        if error: return None, error
        temp, error = self.make_tree_of_assign(execute_node)
        if error: return None, error
        return execute_node, None

    def operator_basic(self, parent, operator = None): # 이항연산
        if not operator: operator = self.current_tok.string
        node = Node("operator", token = None)
        if operator == ".": operator = "dot"
        elif operator == "-":
            front_tok = self.reverse()
            self.advance()
            if front_tok.type != 1 and front_tok.type != 2 and front_tok.string != ")": # Not number and not variable and not function
                tok = self.advance()
                if tok.type == 2:
                    Node("-", parent=node, token = self.current_tok)
                    Node("0", parent=node, token = self.current_tok)
                    Node(tok.string, parent=node, token = self.current_tok)
                    return node, None
                self.reverse()
        Node(operator, parent=node, token = self.current_tok)
        front_node = parent.children[-1]


        back_priority = OPERATOR_PRIORITY[operator]
        front_priority = None
        temp_node = front_node
        if front_node.name == "operator":
            front_operator = front_node.children[0].name
            front_priority = OPERATOR_PRIORITY[front_operator]
        return_is_front = temp_node.name == "operator" and front_priority < back_priority
        while temp_node.name == "operator" and front_priority < back_priority:
            if front_priority < back_priority: # 앞의 연산이 우선순위가 더 높음
                temp_node = temp_node.children[-1]
            if temp_node.name != "operator": # 피연산자를 마주침
                node.parent = temp_node.parent
                temp_node.parent = node
                break
            front_operator = temp_node.children[0].name # 리턴할 노드 업데이트
            front_priority = OPERATOR_PRIORITY[front_operator]
            if front_priority >= back_priority:
                node.parent = temp_node.parent
                temp_node.parent = node
                break
        else:
            front_node.parent = node
        self.advance()
        back_node, error = self.build_ast(node)
        if error: return node, error

        if return_is_front: return front_node, error
        else: return node, error
    def operator_big_paren(self, parent): # [
        pre_token = self.reverse()
        self.advance()
        if pre_token.type == 1 or pre_token.string == "]" or pre_token.string == ")": return self.operator_basic(parent, "member")
        else: return self.operator_make_array()
    def operator_small_paren(self, parent):
        node = Node("operator", token = None)
        Node("paren", parent=node, token = self.current_tok)
        self.advance()
        while self.current_tok.string != ")":
            temp, error = self.build_ast(node)
            if error: return None, error
            self.advance()
        return node, None
    def operator_make_array(self):
        node = Node("make_array", token = self.current_tok)
        while True:
            tok = self.advance()
            if tok.string == ",": continue
            elif tok.string == "]": break
            # elif tok.string == "[": depth += 1
            temp, error = self.build_ast(node)
            if error: return None, error
        # self.reverse()
        return node, None
    def operator_member(self, parent):
        pre_node = parent.children[-1]

        node = Node("operator", token = None)
        Node("member", parent=node, token = self.current_tok)
        pre_node.parent = node
        while self.current_tok.string != "]":
            self.advance()
            if self.current_tok.string == ",": return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"Member operator can't contain \",\""
            )
            temp, error = self.build_ast(node)
            if error: return None, error
        return node, error
    def operator_nbt(self, parent):
        node = Node("make_nbt", token = self.current_tok)
        while True:
            tok = self.advance()
            while self.current_tok.string == "\n": tok = self.advance()
            if tok.string == "}": return node, None # 종료조건
            if tok.type != 1 and tok.type != 3:
                return None, InvalidSyntaxError(
                    tok,
                    self.filename,
                    "name type was expected, but it's not"
                )
            key = tok.string
            if tok.type == 3:
                key = key[1:-1]
            key_node = Node(key, parent=node, token = self.current_tok)
            error = self.is_next_match(":")
            if error: return None, error
            self.advance()
            while self.current_tok.string == "\n": self.advance()

            if self.current_tok.string == "," or self.current_tok.string == "}":
                return None, InvalidSyntaxError(
                    self.current_tok,
                    self.filename,
                    "value is missing"
                )
            
            while self.current_tok.string != "," and self.current_tok.string != "}":
                if self.current_tok.string == ":":
                    return None, InvalidSyntaxError(
                        self.current_tok,
                        self.filename,
                        "prior \",\" is missing"
                    )
                temp, error = self.build_ast(key_node)
                if error: return None, error

                self.advance()
            
            if self.current_tok.string == "}": break
        return node, None
    def operator_entity(self, parent):
        tok = self.advance()
        token = tok
        if tok.string not in MINECRAFT_SELECTOR: return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"Minecraft selector char is must be a, p, s, r or e"
            )
        result = "@" + tok.string
        tok = self.advance()
        node = Node("make_selector", token = None)
        if tok.string == "[":
            while tok.string != "]":
                result += tok.string
                tok = self.advance()
        if "[" in result: result += "]"
        Node(result, parent=node, token = token)
        self.reverse()
        return node, None
    def operator_not(self, parent):
        node = Node("operator", token="")
        Node("!", parent=node, token=self.current_tok)
        tok = self.advance()
        if tok.string != "(":
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                "\"(\" was expected, but it's not"
            )
        temp, error = self.build_ast(node)
        if error: return None, error
        return node, None

    def minecraft_command(self):

        command = self.current_tok.line.strip()[1:] # 마크 커맨드 추출
        while self.current_tok.type != 4 and self.current_tok.string != "\n":
            self.advance()
        temp = Node("command", token = self.current_tok)
        Node(command, parent=temp, token = None)
        return temp, None

    def define_var(self):
        type_ = self.current_tok.string
        self.advance()
        if self.current_tok.type != 1:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                "Variable's name was expected, but it's not"
            )

        var = Variable(self.current_tok.string, type_, False)
        self.variables[var.name] = var


        node = Node("define_var", token = None)

        Node(var.name, parent=node, token = self.current_tok)


        return node, None
    def define_const(self):
        type_ = self.current_tok.string
        self.advance()
        if self.current_tok.type != 1:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                "Variable's name was expected, but it's not"
            )

        var = Variable(self.current_tok.string, type_, False)
        self.variables[var.name] = var


        node = Node("define_const", token = None)

        Node(var.name, parent=node, token = self.current_tok)


        return node, None

    def is_next_match(self, target):
        tok = self.advance()
        while tok.string == "\n" or tok.type == 4 and tok.type != 0: tok = self.advance()
        if tok.string != target: return InvalidSyntaxError(
            self.current_tok,
            self.filename,
            f"\"{target}\" was expected, but it's not"
        )
        return None

#######################################
# VARIABLE
#######################################

class Variable:
    def __init__(self, name, type_, is_const, temp = "", details = None) -> None:
        self.name = name
        self.type = type_
        self.is_const = is_const
        self.temp = temp
        self.details = details
        self.value = False

    def __str__(self):
        return f"({self.name}, {self.type}, {self.is_const}, {self.temp}, {self.value})"

class Function:
    def __init__(self, name, type_, inputs, temp) -> None:
        self.name = name
        self.type = type_
        self.inputs = inputs
        self.temp = temp
    def __repr__(self) -> str:
        return f"name: {self.name}, temp: {self.temp}, inputs: {self.inputs}"

#######################################
# INTERPRETER
#######################################

def make_basic_files(version, file_dir, namespace = "pack"):
    function_folder = "function"
    if version[:4] == "1.20": function_folder = "functions"

    # if os.path.exists(file_dir + f"{namespace}/data/{namespace}/{function_folder}"): shutil.rmtree(file_dir + f"{namespace}/data/{namespace}/{function_folder}")
    if os.path.exists(file_dir + f"{namespace}"): shutil.rmtree(file_dir + f"{namespace}")

    tag_folder_dir = file_dir + f"{namespace}/data/minecraft/tags/{function_folder}"
    function_folder_dir = file_dir + f"{namespace}/data/{namespace}/{function_folder}"
    if not os.path.exists(tag_folder_dir): os.makedirs(tag_folder_dir)
    if not os.path.exists(function_folder_dir): os.makedirs(function_folder_dir)

    file = open(file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/load.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:load\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/minecraft/tags/{function_folder}/tick.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:tick\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/{function_folder}/load.mcfunction", "w+")
    file.write(f"\
# This data pack was compiled with the 40planet's compiler.\n\
# https://github.com/alexmonkey05/Datapack-Compiler\n\n")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/{function_folder}/tick.mcfunction", "w+")
    file.close()
    file = open(file_dir + f"{namespace}/pack.mcmeta", "w+")
    datapack_versions = {
        "1.20.4": "26",
        "1.20.6": "41",
        "1.21": "48",
        "1.21.1": "48"
    }
    file.write('{ "pack": {"pack_format": ' + datapack_versions[version] + ', "description": "by 40planet"} }')
    file.close()

class Interpreter:
    def __init__(self, version, root, current_dir = "", result_dir = "./", namespace = "pack", filename = "") -> None:
        self.version = version
        self.function_folder = "function"
        if version[:4] == "1.20": self.function_folder = "functions"


        self.root = root
        self.current_node = root
        self.result_dir = result_dir
        self.filename = filename
        self.namespace = namespace
        self.current_dir = result_dir + f"{self.namespace}/data/{self.namespace}/{self.function_folder}/" + current_dir
        self.current_file = "load.mcfunction"
        self.variables = {
            "false":[Variable("false","bool",True,"false")],
            "true":[Variable("true","bool",True,"true")],
            "var_temp":[Variable("var_temp","bool",True,"var_temp")]
        }
        self.functions = {}
        self.modules = {}

        self.dump_function_cnt = 0
        self.using_variables = [{}]
        self.is_parameter = False
        folder_name = self.filename.split("/")[-1][:-7] + "/"
        if folder_name == self.current_dir.split(f"{self.function_folder}/")[-1]:
            self.is_module = True
        else:
            self.is_module = False

        self.const = []
        self.used_return = {}
        self.used_break = []


    def interprete(self, node, current_dir = None, current_file = None):
        if node.name == "root" or node.name == "assign":
            for child in node.children:
                var_name, error = self.interprete(child)
                if error: return None, error
            return None, None
        if current_dir: self.current_dir = current_dir
        if current_file: self.current_file = current_file

        if node.name in self.variables:
            return self.variables[node.name][-1].temp, None

        method = getattr(self, node.name + "_")
        var_name, error = method(node)
        if error: return None, error
        return var_name, None
    def define_var_(self, node):
        var_name = node.children[0].name
        var = Variable(var_name, "type_", False, get_var_temp())
        self.const.append(var)
        if var.name in self.using_variables[-1]:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"\"{var.name}\" already defined"
            )
        if var.name not in self.variables: self.variables[var.name] = []
        self.variables[var.name].append(var)
        self.using_variables[-1][var.name] = var
        if self.is_parameter: return var, None
        return var, None
    def define_const_(self, node):
        var_name = node.children[0].name
        var = Variable(var_name, "type_", True, get_var_temp())
        self.const.append(var)
        if var.name in self.using_variables[-1]:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"\"{var.name}\" already defined"
            )
        if var.name not in self.variables: self.variables[var.name] = []
        self.variables[var.name].append(var)
        self.using_variables[-1][var.name] = var
        if self.is_parameter: return var, None
        return var, None
    def define_function_(self, node):
        fun = Function(node.children[1].name, node.children[0].name, [], get_fun_temp())
        self.functions[fun.name] = fun
        inputs = node.children[2].children
        self.using_variables.append({})
        self.is_parameter = True
        for input_node in inputs:
            var, error = self.interprete(input_node)
            if error: return None, error
            fun.inputs.append(var)
            self.using_variables[-1][var.name] = var
            if var.name not in self.variables: self.variables[var.name] = []
        self.is_parameter = False
        currrent_file = self.current_file
        self.current_file = fun.name + ".mcfunction"
        for child in node.children[3].children:
            temp, error = self.interprete(child)
            if error: return None, error

        self.current_file = currrent_file
        for var in self.using_variables[-1]:
            used_var_temp.append(self.using_variables[-1][var].temp)
            if var == "0": continue
            self.variables[var].pop(-1)
            if len(self.variables[var]) == 0:
                del(self.variables[var])
        self.using_variables.pop(-1)
        self.variables[fun.temp] = [Variable(fun.name, fun.type, False, fun.temp)]
        reset_return_score = ""
        for temp in self.used_return:
            reset_return_score += f"scoreboard players set #{temp} {SCOREBOARD_NAME} 0\n"
        filename = self.current_dir + fun.name + ".mcfunction"
        if not os.path.isfile(filename): open(filename, 'w+', encoding="utf-8").close()
        with open(filename, 'r+', encoding="utf-8") as file:
            file_data = file.read()
            file.seek(0, 0)
            file.write(reset_return_score + file_data)
        self.used_return = {}
        return None, None
    def call_function_(self, node):
        input_nodes = node.children[1].children
        if node.children[0].name in BUILT_IN_FUNCTION:
            method_name = f'fun_{node.children[0].name}'
            method = getattr(self, method_name)
            var_name, error = method(node, input_nodes)
            if error: return None, error
            return var_name, None
        fun = self.functions[node.children[0].name]
        if len(fun.inputs) != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"{fun.name} must have only {len(fun.inputs)} parameters"
            )
        file = open(self.current_dir + self.current_file, "a", encoding="utf-8")
        for i in range(len(fun.inputs)):
            var = fun.inputs[i]
            value = input_nodes[i].children[0]
            temp = value.name
            if temp in INTERPRETE_THESE:
                temp, error = self.interprete(value)
                if error: return None, error
            if temp in self.variables:
                self.write(f"data modify storage {STORAGE_NAME} {var.temp} set from storage {STORAGE_NAME} {self.variables[temp][-1].temp}\n")
            else:
                self.write(f"data modify storage {STORAGE_NAME} {var.temp} set value {temp}\n")

        file.write(f"function {self.namespace}:{self.get_folder_dir()}{fun.name}\n")
        file.close()
        return fun.temp, None
    def import_(self, node):
        name = node.children[0].name
        try:
            os.makedirs(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/")
        except:
            return None, None
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/load.mcfunction", "w+").close()
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/tick.mcfunction", "w+").close()
        with open(self.result_dir + f"{self.namespace}/data/minecraft/tags/{self.function_folder}/load.json") as f:
            data = json.load(f)
            data["values"].append(f"{self.namespace}:{name}/load")
            file = open(self.result_dir + f"{self.namespace}/data/minecraft/tags/{self.function_folder}/load.json", "w+")
            file.write(str(data).replace("\'", "\""))
            file.close()
        with open(self.result_dir + f"{self.namespace}/data/minecraft/tags/{self.function_folder}/tick.json") as f:
            data = json.load(f)
            data["values"].append(f"{self.namespace}:{name}/tick")
            file = open(self.result_dir + f"{self.namespace}/data/minecraft/tags/{self.function_folder}/tick.json", "w+")
            file.write(str(data).replace("\'", "\""))
            file.close()
        details, error = interprete("/".join(self.filename.split("/")[:-1]) + "/" + name, self.version, self.result_dir, self.namespace, True, node.children[0].token)
        if error: return None, error
        self.variables[name] = [Variable(name, "module", False)]
        self.modules[name] = details
        for fun_name in details["functions"]:
            fun = details["functions"][fun_name]
            self.variables[fun.temp] = [Variable(fun.name, fun.type, False, fun.temp)]
            self.functions[f"{name}.{fun.name}"] = Function(f"{name}/{fun.name}", fun.type, fun.inputs, fun.temp)
        for var_name in details["variables"]:
            var = details["variables"][var_name][0]
            if var_name == var.temp: continue
            self.variables[f"{name}.{var.name}"] = [var]
        return None, None
    def if_(self, node, type = "if"):
        if_score, error = self.interprete(node.children[0].children[0]) # interprete condition
        if error: return None, error
        temp = get_temp()

        current_file = self.current_file
        dump_function = self.make_dump_function()
        self.write(f"execute store result score #{temp} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {if_score}\nexecute if score #{temp} {SCOREBOARD_NAME} matches 1.. run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
        self.current_file = dump_function
        self.using_variables.append({})

        for child in node.children[1].children:
            temp_, error = self.interprete(child) # interprete assign
            if error: return None, error

        self.current_file = current_file

        if type == "if": self.break_and_return(node)

        for var in self.using_variables[-1]:
            used_var_temp.append(self.using_variables[-1][var].temp)
            if var == "0": continue
            self.variables[var].pop(-1)
            if len(self.variables[var]) == 0:
                del(self.variables[var])
        self.using_variables.pop(-1)

        if len(node.children) >= 3:

            dump_function = self.make_dump_function()
            self.write(f"execute unless score #{temp} {SCOREBOARD_NAME} matches 1.. run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
            current_file = self.current_file
            self.current_file = dump_function
            self.using_variables.append({})

            for child in node.children[2].children:
                temp_, error = self.interprete(child) # interprete assign
                if error: return None, error
            self.current_file = current_file
            for var in self.using_variables[-1]:
                used_var_temp.append(self.using_variables[-1][var].temp)
                if var == "0": continue
                self.variables[var].pop(-1)
                if len(self.variables[var]) == 0:
                    del(self.variables[var])
            self.using_variables.pop(-1)

        self.add_used_temp(if_score)
        self.add_used_temp(temp)
        return dump_function, None
    def while_(self, node):
        dump_function, error = self.if_(node, "while")
        if error: return None, error
        current_file = self.current_file
        self.current_file = dump_function

        if_score, error = self.interprete(node.children[0].children[0]) # interprete condition
        if error: return None, error
        for temp in self.used_break:
            self.write(f"scoreboard players set #{temp} {SCOREBOARD_NAME} 0\n")
        self.write(f"execute store result score #{if_score} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {if_score}\nexecute if score #{if_score} {SCOREBOARD_NAME} matches 1.. run function {self.namespace}:{self.get_folder_dir()}{self.current_file[:-11]}\n")
        self.current_file = current_file
        return None, None
    def operator_(self, node):
        operator = node.children[0].name
        if operator == "paren":
            return self.interprete(node.children[1])
        method_name = f'operator_{OPERATOR_TO_STRING[operator]}'
        method = getattr(self, method_name)
        var_name, error = method(node)
        if error: return None, error
        # if "." in var_name and operator != "dot":
        #     var = self.variables[var_name][-1]
        #     if var.type in SCORE_TYPES:
        #         if var.type == "int" or var.type == "bool": self.write(f"execute store result storage {STORAGE_NAME} {var.temp} int 1 run scoreboard players get #{var.temp} {SCOREBOARD_NAME}\n")
        #         else: self.write(f"execute store result storage {STORAGE_NAME} {var.temp} {var.type[0]} 0.01 run scoreboard players get #{var.temp} {SCOREBOARD_NAME}\n")
        return var_name, error
    def command_(self, node):
        command = node.children[0].name
        if NAMESPACE + ":" in command:
            namespace = self.namespace + ":"
            if self.is_module:
                namespace += self.filename.split("/")[-1][:-7] + "/"
            command = command.replace(NAMESPACE + ":", namespace)
        if "^" in command and "&" in command:
            command, error = self.macro_(command, node.token)
            if error: return None, error
            if command[0] != "$": command = "$" + command
            self.macro(command + "\n")
        else:
            self.write(command + "\n")
        return None, None
    def macro_(self, command, token):
        global used_temp
        while "^" in command and "&" in command:
            var_name = ""
            is_var_name = True
            for char in command:
                if char != "^" and is_var_name: continue
                is_var_name = False

                if char == "&":
                    break
                if char != "^":
                    var_name += char
            if var_name not in self.variables:
                return None, InvalidSyntaxError(
                    token,
                    self.filename,
                    f"\"{var_name}\" was not defined"
                )
            command = command.replace("^" + var_name + "&", f"$({self.variables[var_name][-1].temp[5:]})")
        return command, None
    def make_array_(self, node):
        temp = get_temp()
        is_first = True
        elements = ""
        for child in node.children:
            temp2 = child.name
            if temp2 in INTERPRETE_THESE:
                temp2, error = self.interprete(child)
                if error: return None, error
            if is_first:
                if temp2 in self.variables:
                    is_first = False
                    self.write(f"data modify storage {STORAGE_NAME} {temp} set value [{elements[2:]}]\n")
                else:
                    elements += f", {temp2}"
                    continue
            
            temp2 = self.to_storage(temp2)
            self.write(f"data modify storage {STORAGE_NAME} {temp} append from storage {STORAGE_NAME} {temp2}\n")
            self.add_used_temp(temp2)
        if is_first: self.write(f"data modify storage {STORAGE_NAME} {temp} set value [{elements[2:]}]\n")

        if temp not in self.variables: self.variables[temp] = []
        self.variables[temp].append(Variable(temp, "arr", True, temp))
        return temp, None
    def make_nbt_(self, node):
        temp = get_temp()
        elements = "{"
        self.write(f"data remove storage {STORAGE_NAME} {temp}\ndata modify storage {STORAGE_NAME} {temp} set value {{}}\n")
        keys = []
        for child in node.children:
            key = child.name
            value = child.children[0].name
            if value in INTERPRETE_THESE:
                value, error = self.interprete(child.children[0])
                if error: return None, error
            # value = value.replace("\"", "\\\"")
            keys.append(f"{temp}.{key}")
            if value in self.variables:
                var_temp = self.to_storage(value)
                self.write(f"data modify storage {STORAGE_NAME} {temp}.{key} set from storage {STORAGE_NAME} {var_temp}\n")
                if value in self.variables:
                    self.add_var(f"{temp}.{key}", "var_type", self.variables[value][-1].is_const, value)
                else: self.add_var(f"{temp}.{key}", "asdf", False, var_temp)
            else:
                self.write(f"data modify storage {STORAGE_NAME} {temp}.{key} set value {value}\n")
        #         elements += f"\"{key}\":{value},"

        # if len(elements) > 1: elements = elements[:-1] 
        # elements += "}"

        self.add_var(temp, "nbt", False, temp, keys)
        return temp, None
    def make_selector_(self, node):
        temp = get_temp()
        command = node.children[0].name
        if "^" in command and "&" in command:
            command = self.macro_(command, node.token)
            self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value \"" + command.replace("\"", "\\\"") + "\"\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value \"" + command.replace("\"", "\\\"") + "\"\n")
        self.add_var(temp, "entity", False, temp)
        return temp, None
    def operator_return(self, node):
        node.children[0].parent = None
        fun_name = self.current_file[:-11]
        temp_node = None
        temp = get_temp()
        if fun_name not in self.functions:
            temp_node = node
            while temp_node.name != "define_function" and temp_node.name != "function":
                temp_node = temp_node.parent
                if temp_node.name == "root":
                    return None, InvalidSyntaxError(
                        temp_node.token,
                        self.filename,
                        f"\"return\" must in function"
                    )
            fun_name = temp_node.children[1].name
        return_node = node.children[0]
        return_value = return_node.name
        if return_value in INTERPRETE_THESE:
            return_value, error = self.interprete(return_node)
            if error: return None, error
        if temp_node and temp_node.name == "define_function":
            fun = self.functions[fun_name]

            if return_value in self.variables:
                self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set from storage {STORAGE_NAME} {self.variables[return_value][-1].temp}\nscoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn run data get storage {STORAGE_NAME} {fun.temp}\n")
            else:
                self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set value {return_value}\nscoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn {return_value}\n")
            self.used_return[temp] = fun.temp
            return fun.temp, None
        else:
            fun = self.functions[fun_name]
            if return_value in self.variables:
                self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set from storage {STORAGE_NAME} {self.variables[return_value][-1].temp}\nscoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn run data get storage {STORAGE_NAME} {fun.temp}\n")
            else:
                self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set value {return_value}\nscoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn {return_value}\n")
            return fun_name, None
    def break_(self, node):
        temp_node = node
        while temp_node.name != "while":
            temp_node = temp_node.parent
            if temp_node.name == "root":
                return None, InvalidSyntaxError(
                    temp_node.token,
                    self.filename,
                    f"\"break\" must in while"
                )
        temp = get_temp()
        self.write(f"scoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn 0\n")
        self.used_break.append(temp)
        return None, None
    def execute_(self, node):
        execute = Execute(node.children[0], self, node.token)
        command, error = execute.interprete()
        if error: return None, error


        current_file = self.current_file
        dump_function = self.make_dump_function()
        if command[0] == "$":
            self.macro(f"{command}run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
        else:
            self.write(f"{command}run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
        self.current_file = dump_function
        self.using_variables.append({})

        for child in node.children[1].children:
            temp, error = self.interprete(child) # interprete assign
            if error: return None, error

        self.current_file = current_file
        self.break_and_return(node)
        for var in self.using_variables[-1]:
            used_var_temp.append(self.using_variables[-1][var].temp)
            if var == "0": continue
            self.variables[var].pop(-1)
            if len(self.variables[var]) == 0:
                del(self.variables[var])
        self.using_variables.pop(-1)


        return None, None

    def break_and_return(self, node):
        for temp in self.used_return:
            self.write(f"execute if score #{temp} {SCOREBOARD_NAME} matches 1 run return run data get storage {STORAGE_NAME} {self.used_return[temp]}\n")
            self.write_first(f"scoreboard players set #{temp} {SCOREBOARD_NAME} 0\n")
        for temp in self.used_break:
            self.write(f"execute if score #{temp} {SCOREBOARD_NAME} matches 1 run return 0\n")
            self.write_first(f"scoreboard players set #{temp} {SCOREBOARD_NAME} 0\n")
        
        while node.name != "root":
            node = node.parent
            if node.name == "define_function":
                self.used_return = {}
            elif node.name == "while":
                self.used_break = []
            elif node.name == "if" or node.name == "execute": return

    def write_first(self, txt):
        file = open(self.current_dir + self.current_file, "r", encoding="utf-8")
        file_contents = file.read()
        file.close()
        file = open(self.current_dir + self.current_file, "w", encoding="utf-8")
        if txt[0] != "$" and "$(" in txt: self.macro("$" + txt)
        else: file.write(txt)
        file.close()
        self.write(file_contents)



    def operator_equal(self, node):
        var1 = node.children[1].name

        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(node.children[1])
            if error: return None, error
        if var1.__class__ == Variable:
            var1 = var1.name



        var2 = node.children[2].name
        var2_tok = node.children[2].token
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(node.children[2])
            if error: return None, error

        if node.children[1].name == "define_var" and var2[:4] != "temp":
            self.variables[var1][-1].value = var2

        if var1 not in self.variables:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"\"{var1}\" is not defined"
            )

        if var2 in self.variables:
            self.write(f"data modify storage {STORAGE_NAME} {self.variables[var1][-1].temp} set from storage {STORAGE_NAME} {self.variables[var2][-1].temp}\n")
        elif "." in var2 and var2_tok.type != 2:
            self.write(f"data modify storage {STORAGE_NAME} {self.variables[var1][-1].temp} set from storage {STORAGE_NAME} {var2}\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {self.variables[var1][-1].temp} set value {var2}\n")

        self.add_used_temp(var2)
        return var1, None
    def operator_basic(self, node):
        operator = node.children[0].name
        var1 = node.children[1].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(node.children[1])
            if error: return None, error

        var2 = node.children[2].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(node.children[2])
            if error: return None, error

        temp = get_temp()
        if var1 != "var1":
            if var1 in self.variables: self.write(f"data modify storage {STORAGE_NAME} var1 set from storage {STORAGE_NAME} {self.variables[var1][-1].temp}\n")
            else: self.write(f"data modify storage {STORAGE_NAME} var1 set value {var1}\n")
        if var2 in self.variables: self.write(f"data modify storage {STORAGE_NAME} var2 set from storage {STORAGE_NAME} {self.variables[var2][-1].temp}\n")
        else: self.write(f"data modify storage {STORAGE_NAME} var2 set value {var2}\n")
        self.write(f"scoreboard players set #operator_type {SCOREBOARD_NAME} {OPERATOR_ID[operator]}\nfunction basic:operation\ndata modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n")
        self.add_var(temp, "temp", False, temp)
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        return temp, None
    def operator_and_or(self, node):

        temp = get_temp()
        var1 = node.children[1].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(node.children[1])
            if error: return None, error

        var2 = node.children[2].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(node.children[2])
            if error: return None, error

        temp1 = get_temp()
        temp2 = get_temp()
        self.write(f"\
execute store result score #{temp1} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {var1}\n\
execute store result score #{temp2} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {var2}\n\
execute store result storage {STORAGE_NAME} {temp} byte 1 run scoreboard players operation #{temp1} {SCOREBOARD_NAME} *= #{temp2} {SCOREBOARD_NAME}\n\
")
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        self.add_used_temp(temp1)
        self.add_used_temp(temp2)
        return temp, None
    def operator_member(self, node):
        arr = node.children[1].name
        if arr in INTERPRETE_THESE:
            arr, error = self.interprete(node.children[1])
            if error: return None, error

        if arr not in self.variables:
            return None, InvalidSyntaxError(
                node.children[1].token,
                self.filename,
                f"{arr} is not defined"
            )
        arr = self.variables[arr][-1].temp
        index = node.children[2].name
        if index in INTERPRETE_THESE:
            index, error = self.interprete(node.children[2])
            if error: return None, error
        if index in self.variables: arr += f"[$({self.variables[index][-1].temp[5:]})]"
        elif index[0] == "\"": arr += f"[{index[1:-1]}]"
        else: arr += f"[{index}]"

        self.add_var(arr, "type", False, arr)
        self.add_used_temp(index)
        return arr, None
    def operator_not(self, node):
        temp, error = self.interprete(node.children[1])
        if error: return None, error
        self.write(f"execute store result score #{temp} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {temp}\nexecute store result storage {STORAGE_NAME} {temp} byte 1 if score #{temp} {SCOREBOARD_NAME} matches ..0\n")
        self.add_var(temp, "bool", False, temp)
        return temp, None
    def operator_dot(self, node):
        var1_node = node.children[1]
        var2_node = node.children[2]


        var1 = var1_node.name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(var1_node)
            if error: return None, error
        var2 = var2_node.name
        if var2 == "operator":
            var2, error = self.interprete(var2_node)
            if error: return None, error


        if var2 == "call_function": # 메소드
            pass
        if var1 in self.modules:
            if var2 == "call_function": # 메소드
                var2_node.children[0].name = var1 + "." + var2_node.children[0].name
                return self.interprete(var2_node)
            else:
                result = f"{var1}.{var2}"
                if result not in self.variables:
                    return None, InvalidSyntaxError(
                        var2_node.token,
                        self.filename,
                        f"{result} was not defined"
                    )
                return result, None
        elif var1 in self.variables: # 인스턴스
            result = f"{self.variables[var1][-1].temp}.{var2}"
            if result not in self.variables:
                self.variables[result] = [Variable(result, "asdf", False, result)]
            return result, None
        else: # 모듈 또는 클래스

            return None, InvalidSyntaxError(
                var1_node.token,
                self.filename,
                f"{var1} was not defined"
            )

    def fun_print(self, node, input_nodes):
        result_arr = []
        dump_file = None
        for input_node in input_nodes:
            temp = input_node.children[0].name
            if temp == "make_selector":
                
                if "^" in input_node.children[0].children[0].name:
                    temp, error = self.interprete(input_node.children[0])
                    dump_file = True
                    result_arr.append('{"selector":"$(%s)"}' % self.variables[temp][-1].temp)
                else: result_arr.append('{"selector":"%s"}' % input_node.children[0].children[0].name)
                continue
            elif temp in INTERPRETE_THESE:
                temp, error = self.interprete(input_node.children[0])
                if error: return None, error
            if temp in self.variables:
                result_arr.append('{"nbt":"%s","storage":"%s"}' % (self.variables[temp][-1].temp, STORAGE_NAME))
            else:
                if temp[0] == "\"": temp = temp[1:-1]
                elif temp[0] not in DIGITS:
                    return None, InvalidSyntaxError(
                        input_node.children[0].token,
                        self.filename,
                        f"{temp} is not defined"
                    )
                result_arr.append('{"text":"%s"}' % temp.replace("\"", "\\\""))
        result = ""
        for string in result_arr:
            result += string + ",\" \", "
        result = "tellraw @a [" + result[:-6] + "]\n"
        if dump_file: self.macro("$" + result)
        else: self.write(result)
        self.add_used_temp(temp)
        return "0", None
    def fun_random(self, node, input_nodes):
        if 0 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"random must have only 0 parameters"
            )
        temp = get_temp()
        self.write(f"execute store result storage {STORAGE_NAME} {temp} float 0.001 run random value 0..1000\n")
        self.add_var(temp, "int", False, temp)
        return temp, None
    def fun_type(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"type must have only 1 parameters"
            )
        var_name = input_nodes[0].children[0].name
        temp = get_temp()
        self.write(f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {self.variables[var_name][-1].temp}\n\
execute store result score #{temp} {SCOREBOARD_NAME} run function basic:get_type_score \n\
execute if score #{temp} {SCOREBOARD_NAME} matches 0 run data modify storage {STORAGE_NAME} {temp} set value \"nbt\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 1 run data modify storage {STORAGE_NAME} {temp} set value \"int\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 2 run data modify storage {STORAGE_NAME} {temp} set value \"float\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 3 run data modify storage {STORAGE_NAME} {temp} set value \"double\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 4 run data modify storage {STORAGE_NAME} {temp} set value \"string\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 5 run data modify storage {STORAGE_NAME} {temp} set value \"bool\"\n\
")
        self.add_var(temp, "string", False, temp)
        return temp, None
    def fun_round(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"type must have only 1 parameters"
            )
        var_name = input_nodes[0].children[0].name
        temp = get_temp()
        if var_name in self.variables:
            self.write(f"\
execute store result storage {STORAGE_NAME} {temp} int 1 run data get storage {STORAGE_NAME} {self.variables[var_name][-1].temp}\n\
")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {round(float(var_name))}\n")
        self.add_var(temp, "int", False, temp)
        return temp, None
    def fun_get_score(self, node, input_nodes):
        if 2 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"get_score must have only 2 parameters"
            )
        temp = get_temp()
        var1 = input_nodes[0].children[0].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error
        is_var = False
        if var1 in self.variables:
            var1 = f"$({self.variables[var1][-1].temp[5:]})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var2 = f"$({self.variables[var2][-1].temp[5:]})"
            is_var = True
        elif var2[0] == "\"": var2 = var2[1:-1]
        if is_var:
            self.macro(f"$execute store result storage {STORAGE_NAME} {temp} int 1 run scoreboard players get {var1} {var2}\n")
        else:
            self.write(f"execute store result storage {STORAGE_NAME} {temp} int 1 run scoreboard players get {var1} {var2}\n")
        self.add_var(temp, "int", False, temp)
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        return temp, None
    def fun_get_data(self, node, input_nodes):
        if 3 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"get_data must have only 3 parameters"
            )
        temp = get_temp()
        var1 = input_nodes[0].children[0].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error
        var3 = input_nodes[2].children[0].name
        if var3 in INTERPRETE_THESE:
            var3, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error

        is_var = False
        if var1 in self.variables:
            var1 = f"$({self.variables[var1][-1].temp[5:]})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var2 = f"$({self.variables[var2][-1].temp[5:]})"
            is_var = True
        elif var2[0] == "\"": var2 = var2[1:-1]
        if var3 in self.variables:
            var3 = f"$({self.variables[var3][-1].temp[5:]})"
            is_var = True
        elif var3[0] == "\"": var3 = var3[1:-1]
        if is_var:
            self.macro(f"$data modify storage {STORAGE_NAME} {temp} set from {var1} {var2} {var3}\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set from {var1} {var2} {var3}\n")
        self.add_var(temp, "var4", False, temp)
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        self.add_used_temp(var3)
        return temp, None
    def fun_set_score(self, node, input_nodes):
        if 3 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"set_score must have only 3 parameters"
            )
        var1 = input_nodes[0].children[0].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error
        var3 = input_nodes[2].children[0].name
        if var3 in INTERPRETE_THESE:
            var3, error = self.interprete(input_nodes[2].children[0])
            if error: return None, error

        is_var = False
        if var1 in self.variables:
            is_var = True
            var1 = f"$({self.variables[var1][-1].temp[5:]})"
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            is_var = True
            var2 = f"$({self.variables[var2][-1].temp[5:]})"
        elif var2[0] == "\"": var2 = var2[1:-1]
        if var3 not in self.variables:
            if is_var: self.macro(f"$scoreboard players set {var1} {var2} {var3}\n")
            else: self.write(f"scoreboard players set {var1} {var2} {var3}\n")
        else:
            if is_var: self.macro(f"$execute store result score {var1} {var2} run data get storage {STORAGE_NAME} {self.variables[var3][-1].temp}\n")
            else: self.write(f"execute store result score {var1} {var2} run data get storage {STORAGE_NAME} {self.variables[var3][-1].temp}\n")
        return var3, None
    def fun_set_data(self, node, input_nodes):
        if 4 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"get_data must have only 4 parameters"
            )
        temp = get_temp()
        var1 = input_nodes[0].children[0].name
        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error
        var3 = input_nodes[2].children[0].name
        if var3 in INTERPRETE_THESE:
            var3, error = self.interprete(input_nodes[2].children[0])
            if error: return None, error
        var4 = input_nodes[3].children[0].name
        if var4 in INTERPRETE_THESE:
            var4, error = self.interprete(input_nodes[3].children[0])
            if error: return None, error

        if var1 not in self.variables and var1 not in ('"entity"', '"block"', '"storage"'):
            return None, InvalidSyntaxError(
                    node.children[0].token,
                    self.filename,
                    f"from parameters must be \"block\", \"entity\" or \"stoage\""
                )
        is_var = False
        if var1 in self.variables:
            var1 = f"$({self.variables[var1][-1].temp[5:]})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var1 = f"$({self.variables[var2][-1].temp[5:]})"
            is_var = True
        elif var2[0] == "\"": var2 = var2[1:-1]
        if var3 in self.variables:
            var3 = f"$({self.variables[var3][-1].temp[5:]})"
            is_var = True
        elif var3[0] == "\"": var3 = var3[1:-1]
        if var4 in self.variables:
            if is_var:
                self.macro(f"$data modify {var1} {var2} {var3} set from storage {STORAGE_NAME} {self.variables[var4][-1].temp}\n")
            else:
                self.write(f"data modify {var1} {var2} {var3} set from storage {STORAGE_NAME} {self.variables[var4][-1].temp}\n")
        else:
            if is_var:
                self.macro(f"$data modify {var1} {var2} {var3} set value {var4}\n")
            else:
                self.write(f"data modify {var1} {var2} {var3} set value {var4}\n")
        self.add_var(temp, "var4", False, temp)
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        self.add_used_temp(var3)
        self.add_used_temp(var4)
        return temp, None
    def fun_int(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"int must have only 1 parameters"
            )
        input_node = input_nodes[0].children[0]
        var = input_node.name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_node)
            if error: return None, error
        temp = get_temp()
        if var in self.variables:
            self.write(f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {self.variables[var][-1].temp}\n\
execute store result score #type {SCOREBOARD_NAME} run function basic:get_type_score\n\
function basic:int/convert/execute\n\
data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n")
        elif var[0] == "\"":
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var[1:-1]}\n")
        elif var[0] == "@":
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"\"entity\" can not be \"int\""
            )
        elif "." in var:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {round(float(var))}\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var}\n")

        self.add_used_temp(var)
        self.add_var(temp, "int", False, temp)
        return temp, None
    def fun_bool(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"bool must have only 1 parameters"
            )
        input_node = input_nodes[0].children[0]
        var = input_node.name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_node)
            if error: return None, error
        temp = get_temp()
        if var in self.variables:
            self.write(f"execute store result score {SCOREBOARD_NAME} #temp run data get storage {STORAGE_NAME} {self.variables[var][-1].temp}\n\
execute if score #temp {SCOREBOARD_NAME} matches 1.. run data modify storage {STORAGE_NAME} {temp} set value 1b\n\
execute if score #temp {SCOREBOARD_NAME} matches ..0 run data modify storage {STORAGE_NAME} {temp} set value 0b\n")
        elif var[0] == "\"":
            if var == '""': self.write(f"data modify storage {STORAGE_NAME} {temp} set value 0b")
            else: self.write(f"data modify storage {STORAGE_NAME} {temp} set value 1b")
        elif var[0] == "@":
            self.write(f"execute store result score {SCOREBOARD_NAME} #temp if entity {var}\n\
execute if score #temp {SCOREBOARD_NAME} matches 1.. run data modify storage {STORAGE_NAME} {temp} set value 1b\n\
execute if score #temp {SCOREBOARD_NAME} matches ..0 run data modify storage {STORAGE_NAME} {temp} set value 0b\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var == 0}\n")

        self.add_used_temp(var)
        self.add_var(temp, "int", False, temp)
        return temp, None
    def fun_float(self, node, input_nodes, type_ = "float"):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"float must have only 1 parameters"
            )
        input_node = input_nodes[0].children[0]
        var = input_node.name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_node)
            if error: return None, error
        temp = get_temp()
        if var in self.variables:
            self.write(f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {self.variables[var][-1].temp}\n\
execute store result score #type {SCOREBOARD_NAME} run function basic:get_type_score\n\
function basic:{type_}/convert/execute\n\
data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n")
        elif var[0] == "\"":
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var[1:-1]}{type_[0]}\n")
        elif var[0] == "@":
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"\"entity\" can not be \"{type_}\""
            )
        elif "." in var:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {(float(var))}{type_[0]}\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var}{type_[0]}\n")

        self.add_used_temp(var)
        self.add_var(temp, "int", False, temp)
        return temp, None
    def fun_double(self, node, input_nodes):
        return self.fun_float(node, input_nodes, "double")
    def fun_string(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"string must have only 1 parameters"
            )
        input_node = input_nodes[0].children[0]
        var = input_node.name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_node)
            if error: return None, error
        temp = get_temp()
        if var in self.variables:
            self.write(f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {self.variables[var][-1].temp}\n\
execute store result score #type {SCOREBOARD_NAME} run function basic:get_type_score\n\
execute if score #type {SCOREBOARD_NAME} matches 4 run data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} type_var\n\
execute unless score #type {SCOREBOARD_NAME} matches 4 run ")
            self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value \"$({self.variables[var][-1].temp[5:]})\"\n")
        else:
            if var[0] == "\"":
                var = var[1:-1]
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value \"{var}\"\n")
        self.add_used_temp(var)
        self.add_var(temp, "string", False, temp)
        return temp, None
    def fun_entity(self, node, input_nodes):
        return self.fun_string(node, input_nodes)
        # if 1 != len(input_nodes):
        #     return None, InvalidSyntaxError(
        #         node.children[0].token,
        #         self.filename,
        #         f"entity must have only 1 parameters"
        #     )
        # input_node = input_nodes[0].children[0]
        # var = input_node.name
        # if var in INTERPRETE_THESE:
        #     var, error = self.interprete(input_node)
        #     if error: return None, error
        # temp = get_temp()
        # self.add_var(temp, "entity", False, temp)

        # var_type = self.get_type(var)
        # if var_type != "string":
        #     return None, InvalidSyntaxError(
        #         node.children[0].token,
        #         self.filename,
        #         f"\"{var_type}\" can not be \"entity\""
        #     )
        # if var in self.variables:
        #     self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value $({self.variables[var][-1].temp[5:]})")
        # else:
        #     self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value {var}")
        # self.add_used_temp(var)
        # return temp, None
    def fun_del(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"del must have only 1 parameters"
            )
        var = input_nodes[0].children[0].name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error

        if var not in self.variables:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"{var} is not defined"
            )

        temp = get_temp()
        self.write(f"data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} {var}\n")
        self.write(f"data remove storage {STORAGE_NAME} {var}\n")
        self.add_var(temp, "del_return", False, temp)
        return temp, None
    def fun_append(self, node, input_nodes):
        if 2 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"append must have only 2 parameters"
            )
        arr_node = input_nodes[0].children[0]
        arr = arr_node.name
        if arr in INTERPRETE_THESE:
            arr, error = self.interprete(arr_node)
            if error: return None, error
        elif arr not in self.variables:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"{arr} is not defined"
            )
        else: arr = self.variables[arr][-1].temp
        element = input_nodes[1].children[0].name
        if element in INTERPRETE_THESE:
            element, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error

        if element in self.variables:
            self.write(f"data modify storage {STORAGE_NAME} {arr} append from storage {STORAGE_NAME} {self.variables[element][-1].temp}\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {arr} append value {element}\n")
        return arr, None
    def fun_is_module(self, node, input_nodes):
        if 0 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"is_module must have only 0 parameters"
            )
        temp = get_temp()
        if self.is_module:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value 1b\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value 0b\n")
        return temp, None
    def fun_len(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"len must have only 1 parameters"
            )
        var = input_nodes[0].children[0].name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error

        if var not in self.variables:
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"{var} is not defined"
            )

        temp = get_temp()
        self.write(f"execute store result storage {STORAGE_NAME} {temp} int 1 run data get storage {STORAGE_NAME} {self.variables[var][-1].temp}\n")
        self.add_var(temp, "len", False, temp)
        return temp, None
    def fun_devide(self, node, input_nodes):
        if 2 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"devide must have only 2 parameters"
            )
        var = input_nodes[0].children[0].name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error

        if var in self.variables:
            var = self.variables[var][-1].temp
        else:
            var = self.to_storage(var)
        if var2 in self.variables:
            var2 = self.variables[var2][-1].temp
        else:
            var2 = self.to_storage(var2)

        temp = get_temp()
        self.write(f"data modify storage 40planet:calc list set value [0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f]\n\
execute store result storage 40planet:calc list[0] float 0.00001 run data get storage {STORAGE_NAME} {var} 100000\n\
execute store result storage 40planet:calc list[-1] float 0.00001 run data get storage {STORAGE_NAME} {var2} 100000\n\
data modify entity 0-0-0-0-a transformation set from storage 40planet:calc list\n\
data modify storage {STORAGE_NAME} {temp} set from entity 0-0-0-0-a transformation.scale[0]\n")
        self.add_var(temp, "len", False, temp)
        return temp, None
    def fun_multiply(self, node, input_nodes):
        if 2 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"multiply must have only 2 parameters"
            )
        var = input_nodes[0].children[0].name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(input_nodes[0].children[0])
            if error: return None, error

        if var in self.variables:
            var = self.variables[var][-1].temp
        else:
            var = self.to_storage(var)
        if var2 in self.variables:
            var2 = self.variables[var2][-1].temp
        else:
            var2 = self.to_storage(var2)

        temp = get_temp()
        self.write(f"data modify storage 40planet:calc list set value [0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f]\n\
data modify storage 40planet:calc list[0] set value 1f\n\
execute store result storage 40planet:calc list[-1] float 0.00001 run data get storage {STORAGE_NAME} {var} 100000\n\
data modify entity 0-0-0-0-a transformation set from storage 40planet:calc list\n\
\
data modify storage 40planet:calc list set value [0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f]\n\
execute store result storage 40planet:calc list[0] float 0.00001 run data get storage {STORAGE_NAME} {var2} 100000\n\
data modify storage 40planet:calc list[-1] set from entity 0-0-0-0-a transformation.scale[0]\n\
data modify entity 0-0-0-0-a transformation set from storage 40planet:calc list\n\
data modify storage {STORAGE_NAME} {temp} set from entity 0-0-0-0-a transformation.scale[0]\n")
        self.add_var(temp, "len", False, temp)
        return temp, None
    # def fun_sum(self, node, input_nodes):
    #     if 2 != len(input_nodes):
    #         return None, InvalidSyntaxError(
    #             node.children[0].token,
    #             self.filename,
    #             f"sum must have only 2 parameters"
    #         )
    #     var = input_nodes[0].children[0].name
    #     if var in INTERPRETE_THESE:
    #         var, error = self.interprete(input_nodes[0].children[0])
    #         if error: return None, error
    #     if var in self.variables:
    #         var = self.variables[var][-1].temp
    #     else:
    #         var = self.to_storage(var)
    #     var2 = input_nodes[1].children[0].name
    #     if var2 in INTERPRETE_THESE:
    #         var2, error = self.interprete(input_nodes[0].children[0])
    #         if error: return None, error

    #     self.write(f"data modify entity 0-0-0-0-a Pos[1] set from storage {STORAGE_NAME} {var}\n")
    #     if var2 in self.variables:
    #         self.macro(f"$execute as 0-0-0-0-a at @s run tp @s ~ ~$({var2}) ~\n")
    #     else:
    #         self.write(f"execute as 0-0-0-0-a at @s run tp @s ~ ~{var2} ~\n")
    #     temp = get_temp()
    #     self.add_var(temp, "sum", False, temp)
    #     self.write(f"data modify storage {STORAGE_NAME} {temp} set from entity 0-0-0-0-a Pos[1]\n")
    #     return temp, None


    def get_folder_dir(self):
        dir_arr = self.current_dir.split("/")
        dir_arr = dir_arr[dir_arr.index(self.function_folder):]
        folder = "/".join(dir_arr[1:])
        return folder

    def to_storage(self, var):
        if var in self.variables:
            return self.variables[var][-1].temp
        temp = get_temp()
        self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var}\n")
        return temp

    def add_used_temp(self, var):
        if var[:4] == "temp" and len(var) > 4:
            used_temp.append(var)
            if var in self.variables: del(self.variables[var])

    def make_dump_function(self):
        filename = str(self.dump_function_cnt) + ".mcfunction"
        self.dump_function_cnt += 1
        file = open(self.current_dir + filename, "w+")
        file.close()
        return filename

    def write(self, txt):
        if txt[0] != "$" and "$(" in txt: return self.macro("$" + txt)
        file = open(self.current_dir + self.current_file, "a", encoding="utf-8")
        file.write(txt)
        file.close()

    def macro(self, txt):
        current_file = self.current_file
        dump_file = self.make_dump_function()
        self.current_file = dump_file
        self.write(txt)
        self.current_file = current_file
        self.write(f"function {self.namespace}:{self.get_folder_dir()}{dump_file[:-11]} with storage {STORAGE_NAME} data\n")

    def add_var(self, name, type, is_const, temp, details = None):
        if name not in self.variables: self.variables[name] = []
        self.variables[name].append(Variable(name, type, is_const, temp, details))

class Execute:
    def __init__(self, condition, interpreter, token) -> None:
        Node(" ", parent=condition, token="")
        self.condition = condition
        self.arr = self.condition.children
        self.idx = 0
        self.result = "execute "
        self.current_node = self.arr[0]
        self.interpreter = interpreter
        self.len = len(self.arr)

        self.selectors = ["p", "a", "r", "s", "e"]
        if float(interpreter.version[:4]) >= 1.21:
            self.selectors.append("n")

    def interprete(self) -> string:
        while self.len > self.idx:
            if self.current_node.name == " ":
                self.advance()
                if self.len <= self.idx:
                    break
                continue
            method_name = f'execute_{self.current_node.name}'
            method = getattr(self, method_name)
            error = method()
            if error: return None, error
            self.advance()
        return self.result, None

    def advance(self) -> Node:
        self.idx += 1
        if self.len <= self.idx: return self.current_node
        self.current_node = self.arr[self.idx]
        while self.current_node.name == "\n":
            self.idx += 1
            if self.len <= self.idx: return self.current_node
            self.current_node = self.arr[self.idx]
        return self.current_node

    def reverse(self) -> Node:
        self.idx -= 1
        if 0 > self.idx: return self.current_node
        self.current_node = self.arr[self.idx]
        while self.current_node.name == "\n":
            self.idx -= 1
            if 0 > self.idx: return self.current_node
            self.current_node = self.arr[self.idx]
        return self.current_node

    def entity(self, node) -> string:
        if node.name != "@":
            return None, InvalidSyntaxError(
                self.current_node.token,
                self.interpreter.filename,
                f'\"entity\" must be started with \"@\"'
            )
        result = ""

        if node in self.interpreter.variables:
            result = f"$({self.interpreter.variables[node][-1].temp[5:]})"
            if self.result[0] != "$": self.result = "$" + self.result
        else:
            result = node.name
            current_node = self.advance()
            if current_node.name not in self.selectors: return None, InvalidSyntaxError(
                    current_node.token,
                    self.interpreter.filename,
                    f'\"entity\" must be followed one of {self.selectors}'
                )
            result += current_node.name
            current_node = self.advance()
            if current_node.name == "[":
                paren_cnt = 1
                result += "["
                while paren_cnt > 0:
                    current_node = self.advance()
                    if current_node.name == "[": paren_cnt += 1
                    elif current_node.name == "]": paren_cnt -= 1
                    result += current_node.name
            else: self.reverse()
        return result, None
    def set_parameters(self, command, parameters) -> InvalidSyntaxError:
        node = self.advance().name
        if node not in parameters:
            return InvalidSyntaxError(
                self.current_node.token,
                self.interpreter.filename,
                f'\"{command}\" must be followed by one of {parameters}'
            )
        self.result += f"{command} {node} "
    def add_string(self) -> InvalidSyntaxError:
        node = self.advance()
        if node.token.type == 3:
            self.result += f"{node.name[1:-1]} "
        elif node.name not in self.interpreter.variables:
            return InvalidSyntaxError(
                node.token,
                self.interpreter.filename,
                f'\"{node.name}\" is not defined'
            )
        else:
            self.result += f"$({self.interpreter.variables[node.name][-1].temp[5:]}) "
            if self.result[0] != "$": self.result = "$" + self.result
    def namespace(self) -> Node:
        namespace = self.advance().name
        if namespace == NAMESPACE: namespace = self.interpreter.namespace
        is_colon = self.advance().name == ":"
        item = ""
        if is_colon:
            item = f"{namespace}:{self.advance().name}"
        elif namespace[0] == "*":
            item = namespace
            self.reverse()
        else:
            item = f"minecraft:{namespace}"
            self.reverse()
        return item
    def variable(self, node) -> string:
        var_temp = get_temp()
        variables = self.interpreter.variables
        node = variables[node][-1].temp
        current_node = self.advance()
        if current_node.name[0] == "." or current_node.name == "[":
            while current_node.name[0] == "." or current_node.name == "[":
                if current_node.name[0] == ".":
                    if current_node.token.type == 2: node += current_node.name
                    else: node += f".{self.advance().name}"
                else:
                    variable_name = self.advance()
                    if variable_name.name in variables:
                        var, error = self.variable(variable_name.name)
                        if error: return None, error
                        node += f"[$({var})]"
                    elif variable_name.token.type == 2:
                        node += f"[{variable_name.name}]"
                    else: return None, InvalidSyntaxError(
                        variable_name.token,
                        self.interpreter.filename,
                        f'\"{variable_name.name}\" is not defined'
                    )
                    self.advance()
                current_node = self.advance()

        else: self.reverse()
        self.interpreter.write(f"data remove storage {STORAGE_NAME} {var_temp}\n")
        self.interpreter.write(f"data modify storage {STORAGE_NAME} {var_temp} set from storage {STORAGE_NAME} {node}\n")
        used_temp.append(var_temp)
        return var_temp, None


    def execute_as(self):
        node = self.advance()
        entity, error = self.entity(node)
        if error: return error
        self.result += f"as {entity} "
        return None
    def execute_at(self):
        node = self.advance()
        entity, error = self.entity(node)
        if error: return error
        self.result += f"at {entity} "
        return None
    def execute_positioned(self):
        node = self.advance()
        if node == "as":
            node = self.advance()
            entity, error = self.entity(node)
            if error: return error
            self.result += f"positioned as {entity} "
        elif node == "over":
            # set_parameters는 self.result에 추가까지 함
            # 때문에 그냥 return 해버려도 됨
            return self.set_parameters("positoined", ("world_surface", "motion_blocking", "motion_blocking_no_leaves", "ocean_floor"))
        else:
            self.result += f"positioned "
            self.reverse()
            error = self.add_string()
            if error: return error
    def execute_align(self):
        return self.set_parameters("align", ("x", "y", "z", "xy", "xz", "yz", "xyz"))
    def execute_facing(self):
        node = self.advance()
        if node.name == "entity":
            node = self.advance()
            entity, error = self.entity(node)
            if error: return error
            return self.set_parameters(f"facing entity {entity}", ("eyes", "feet"))
        else:
            self.result += f"facing "
            self.reverse()
            error = self.add_string()
            if error: return error
    def execute_rotated(self):
        node = self.advance()
        if node.name == "as":
            node = self.advance()
            entity, error = self.entity(node)
            if error: return error
            self.result += f"rotated as {entity} "
        else:
            self.result += f"rotated "
            self.reverse()
            return self.add_string()
    def execute_anchored(self):
        return self.set_parameters("anchored", ("eyes", "feet"))
    def execute_in(self):
        self.result += f"in {self.namespace()} "
    def execute_summon(self):
        self.result += f"summon {self.namespace()} "
    def execute_on(self):
        return self.set_parameters("on", ("attacker", "controller", "leasher", "origin", "owner", "passengers", "target", "vehicle"))
    def execute_if(self, if_or_unless = "if"):
        error = self.set_parameters(if_or_unless, ("block", "blocks", "entity", "score", "biome", "dimension", "function", "loaded", "predicate", "items", "data"))
        if error: return error
        node = self.current_node.name
        if node == "block" or node == "biome":
            error = self.add_string()
            if error: return error
            self.result += f"{self.namespace()} "
        elif node == "blocks":
            for i in range(3):
                error = self.add_string()
                if error: return error
            self.result = self.result[:-1]
            error = self.set_parameters("", ("all", "masked"))
        elif node == "entity":
            entity, error = self.entity(self.advance())
            if error: return error
            self.result += f"{entity} "
        elif node == "score":
            error = self.add_string()
            if error: return error
            error = self.add_string()
            if error: return error
            node = self.advance().name
            if node == "matches":
                score_range_node = self.advance()
                score_range = score_range_node.name
                result_score_range = score_range
                while is_score_range(score_range):
                    if self.idx >= self.len:
                        break
                    result_score_range = score_range
                    score_range += self.advance().name
                else:
                    self.reverse()

                self.result += f"matches {result_score_range} "
            elif node in ("<", "<=", "=", ">=", ">"):
                self.result += f"{node} "
                error = self.add_string()
                if error: return error
                error = self.add_string()
                if error: return error
            else:
                return InvalidSyntaxError(
                    self.current_node.token,
                    self.interpreter.filename,
                    f'\"<if|unless> score <target> <scoreboard>\" must be followed by one of ("<", "<=", "=", ">=", ">", "matches")'
                )
        elif node == "dimension" or node == "predicate":
            self.result += f"{self.namespace()} "
        elif node == "function":
            if len(self.current_node.children) > 0:
                interpreter = self.interpreter
                current_file = interpreter.current_file
                dump_file = interpreter.make_dump_function()
                interpreter.functions[dump_file[:-11]] = Function(dump_file[:-11], "execute if", [], get_fun_temp())
                interpreter.current_file = dump_file
                assign_node = self.current_node.children[0]
                Node("void", parent=self.current_node, token="")
                Node(dump_file[:-11], parent=self.current_node, token="")
                Node("input", parent=self.current_node, token="")
                assign_node.parent = None
                assign_node.parent = self.current_node
                for child in assign_node.children:
                    temp_, error = interpreter.interprete(child) # interprete assign
                    if error: return error
                interpreter.current_file = current_file
                self.result += f"{interpreter.namespace}:{interpreter.get_folder_dir()}{dump_file[:-11]} "
            else: self.result += f"{self.namespace()} "
        elif node == "loaded":
            error = self.add_string()
            if error: return error
        elif node == "items":
            if self.interpreter.version[:4] == "1.20":
                return InvalidSyntaxError(
                    self.current_node.token,
                    self.interpreter.filename,
                    f'\"execute if items\" is available since version 1.21'
                )
            node = self.advance().name
            self.result += node + " "
            if node == "entity":
                entity, error = self.entity(self.advance())
                if error: return error
                self.result += f"{entity} "
            elif node == "block":
                error = self.add_string()
                if error: return error
            else:
                return InvalidSyntaxError(
                    self.current_node.token,
                    self.interpreter.filename,
                    f'\"<if|unless> items\" must be followed by one of ("entity", "block")'
                )
            slot = self.advance().name
            if slot != "weapon":
                current_node = self.advance()
                if current_node.name[0] != ".": return InvalidSyntaxError(
                    current_node.token,
                    self.interpreter.filename,
                    f'\".\" must come'
                )
                if current_node.token.type == 2: slot += current_node.name
                elif current_node.name == ".":
                    
                    current_node = self.advance()
                    if current_node.name != "*": return InvalidSyntaxError(
                        current_node.token,
                        self.interpreter.filename,
                        f'\"*\" or number must come'
                    )
                    slot += ".*"
            item = self.namespace()
            current_node = self.advance()
            if current_node.name == "[":
                paren_cnt = 1
                item += "["
                while paren_cnt > 0:
                    current_node = self.advance()
                    if current_node.name == "[": paren_cnt += 1
                    elif current_node.name == "]": paren_cnt -= 1
                    item += current_node.name
            else: self.reverse()
            self.result += f"{slot} {item} "
        elif node == "data":
            variables = self.interpreter.variables
            node = self.advance().name
            if node in variables:
                node, error = self.variable(node)
                if error: return error
                self.result += f"storage {STORAGE_NAME} "
            elif node in ("block", "entity", "storage"):
                self.result += f"{node} "

                error = self.add_string()
                if error: return error
                error = self.add_string()
                if error: return error

                return None
            else:
                return InvalidSyntaxError(
                    self.current_node.token,
                    self.interpreter.filename,
                    f'\"{node}\" is not defined'
                )
            self.result += f"{node} "
        else:
            return InvalidSyntaxError(
                self.current_node.token,
                self.interpreter.filename,
                f'unexpected Error in execute'
            )
    def execute_unless(self):
        return self.execute_if("unless")
    def execute_store(self):
        return InvalidSyntaxError(
            self.current_node.token,
            self.interpreter.filename,
            f'\"store\" syntax cannot be used in Comet'
        )

    def store_nbt(self):
        error = self.set_parameters(f"", MINECRAFT_TYPES)
        if error: return error
        node = self.advance()
        if node.token.type != 2:
            return InvalidSyntaxError(
                node.token,
                self.interpreter.filename,
                f'\"{node.name}\" is not decimal'
            )
        self.result += node.name + " "


temp_cnt = 0
used_temp = []
temp_namespace = ""
def get_temp():
    global temp_cnt
    global temp_namespace
    if used_temp.__len__() == 0:
        temp_cnt += 1
        temp = "data.%s_temp%d" % (temp_namespace, temp_cnt)
    else:
        temp = used_temp.pop()
    return temp

fun_temp_cnt = 0
def get_fun_temp():
    global fun_temp_cnt
    global temp_namespace
    fun_temp_cnt += 1
    temp = "data.%s_fun_temp%d" % (temp_namespace, fun_temp_cnt)
    return temp

var_temp_cnt = 0
used_var_temp = []
def get_var_temp():
    global var_temp_cnt
    global temp_namespace
    var_temp_cnt += 1
    temp = "data.%s_var_temp%d" % (temp_namespace, var_temp_cnt)
    return temp



def print_tree(ast):
    for pre, fill, node in RenderTree(ast):
        if node.token:
            print("%s%s" % (pre, node.name), end=" | tok: ")
            print(node.token)
        else:
            print("%s%s" % (pre, node.name))

def interprete(filename, version, result_dir, namespace, is_modul = False, token = None):
    if len(filename) < 7 or filename[-7:] != ".planet": filename += ".planet"
    token_arr = []
    if not os.path.isfile(filename):
        return None, Error(token, f"\"{filename}\" does not exist", filename, "")
    with tokenize.open(filename) as f:
        tokens = tokenize.generate_tokens(f.readline)
        for token in tokens:
            if token.type != 64: token_arr.append(token)
    parser = Parser(token_arr, filename)
    ast, error = parser.parse()
    if error:
        if not is_modul: print("\n\n" + error.as_string())
        return None, error

    # print_tree(ast)

    interpreter = None
    if not is_modul: interpreter = Interpreter(version, ast, result_dir=result_dir, namespace=namespace, filename=filename)
    else: interpreter = Interpreter(version, ast, filename.split("/")[-1][:-7] + "/", result_dir=result_dir, namespace=namespace, filename=filename)
    temp, error = interpreter.interprete(ast)
    if error:
        print("\n\n" + error.as_string())
        return None, error

    return {"variables":interpreter.variables, "functions":interpreter.functions}, None

def generate_datapack(filename, version, result_dir = "./", namespace = "pack"):
    global temp_namespace
    result_dir = result_dir.strip()
    namespace = namespace.strip()
    temp_namespace = namespace
    if result_dir == "" or namespace == "":
        print("\n\nresult directory and namespace can not be empty string\n")
        return
    if result_dir[-1] != "/" and result_dir[-1] != "\\":
        result_dir += "/"
    make_basic_files(version, result_dir, namespace)
    return interprete(filename, version, result_dir, namespace)

def reset_temp():
    global var_temp_cnt
    global used_var_temp
    global fun_temp_cnt
    global temp_cnt
    global used_temp
    var_temp_cnt = 0
    used_var_temp = []
    fun_temp_cnt = 0
    temp_cnt = 0
    used_temp = []

import argparse
values = ["1.20.4", "1.20.6", "1.21", "1.21.1"]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='comet_compiler',
                    description='Compile .planet files')
    parser.add_argument('--cli', action='store_true')      # option that takes a value
    parser.add_argument('-p', '--planet')
    parser.add_argument('-v', '--version')
    parser.add_argument('-d', '--dist')
    parser.add_argument('-n', '--name')
    args = parser.parse_args()
    if args.cli:
        print("==================")
        print("Comet Compiler CLI")
        print("==================")
        v = args.version
        if v not in values:
            print(f"Invalid version: {v} / Required version: {values}")
            sys.exit(0)
        p = args.planet
        d = args.dist
        if p == None:
            print("planet file(-p / --planet) is required")
            sys.exit(0)
        if d == None:
            print("dist folder(-d / --dist) is required")
            sys.exit(0)
        n = args.name
        if n == None: n = "pack"
        
        interprete_result, error = generate_datapack(p, v, d, n)
        if error:
            print(error.as_string())
        else:
            print("done!")


        sys.exit(0)
    # generate_datapack("./rpg_planet/main.planet", "1.21", "./", "rpg")
    # generate_datapack("./rpg_planet/skills.planet", "1.21", "./", "skill")
    # generate_datapack("./example/test.planet", "1.21", "./", "pack")
    

    from tkinter import *
    from tkinter import filedialog
    from tkinter import messagebox
    import tkinter.ttk as ttk


    tk = Tk()
    filename = None
    def event():
        version = combobox.get()
        namespace = entry1.get().strip()
        if namespace == "": namespace = "pack"
        try:
            name = tk.file.name
            dir = tk.dir
            temp, error = generate_datapack(name, version, dir, namespace)
            if error:
                print(error.as_string())
                messagebox.showinfo("name", error.as_string())
            else:
                messagebox.showinfo("name", "done!")
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            messagebox.showinfo("name", f"Unexpected {err=}, {type(err)=}")
        reset_temp()

    def select_planet_file():
        tk.file = filedialog.askopenfile(
            title="파일 선택창",
            filetypes=(('planet files', '*.planet'), ('all files', '*.*'))
        )
        label1.configure(text="File: " + tk.file.name)

    def select_folder():
        tk.dir = filedialog.askdirectory()
        label2.configure(text="Folder: " + tk.dir)

    tk.title('.planet -> datapack Compiler')

    label1 = Label(tk,text='File')
    label1.grid(row=0, column=0)
    label2 = Label(tk,text='Folder')
    label2.grid(row=1, column=0)
    label3 = Label(tk,text='Datapack Name')
    label3.grid(row=2, column=0)


    entry1 = Entry(tk)
    entry1.grid(row=2,column=1)

    btn1 = Button(tk,text='Select',command=select_planet_file).grid(row=0,column=1)
    btn2 = Button(tk,text='Select',command=select_folder).grid(row=1,column=1)
    btn3 = Button(tk,text='Compile',command=event).grid(row=3,column=1)

    combobox = ttk.Combobox(tk,values=values,state="readonly")
    combobox.grid(row=3,column=0)
    combobox.set("1.21.1")

    tk.mainloop()