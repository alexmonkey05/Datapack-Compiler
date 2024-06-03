
import tokenize
from anytree import Node, RenderTree
import os
import string
import shutil
import json

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox





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
SCORE_TYPES = ("int", "float", "double", "byte")
TYPES = ("entity", "nbt", "string") + SCORE_TYPES
MEANS_END = (";", "]", "}")
SCOREBOARD_NAME = "40planet_num"
STORAGE_NAME = "40planet:value"

KEYWORDS = ( "if", "else", "while", "import", "def", "break", "and", "or", "return", "execute", "var" ) # + TYPES

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
    "member":6,
    "dot":6,
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

BUILT_IN_FUNCTION = ("print", "random", "type", "get_score", "get_data", "set_score", "set_data", "round") + TYPES

EXECUTE_KEYWORDS = ( "as", "at", "if", "positioned", "" )

MINECRAFT_TYPES = ("byte", "short", "int", "float", "double", "long")
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
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.filename}, line {self.token.start[0]}'
        result += "\n\n" + self.token.line
        if self.token.line[-1] != "\n": result += "\n"
        result += " " * self.token.start[1]
        result += "^" * (self.token.end[1] - self.token.start[1])
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
        self.variables = {}
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
    
        root = Node("root", token = None)

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
                node, error = self.define_var()
            else:
                method_name = f'make_tree_of_{self.current_tok.string}'
                method = getattr(self, method_name)
                node, error = method(parent)
            return node, error
        elif self.current_tok.string not in self.variables and self.current_tok.string not in self.functions and self.current_tok.string not in BUILT_IN_FUNCTION:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} was not definded"
            )
        elif self.current_tok.string in self.variables:
            node = Node(self.current_tok.string, token = self.current_tok)
            tok = self.advance()
            if tok.string == "[":
                node.parent = parent
                return self.operator_member(parent)
            self.reverse()
            return node, None
        elif self.current_tok.string in self.functions or self.current_tok.string in BUILT_IN_FUNCTION:
            return self.make_tree_of_call_function()
        else:
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"{self.current_tok.string} was unexpected"
            )
    def type_2(self, parent): # NUMBER type
        return Node(self.current_tok.string, token = self.current_tok), None
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
                f"{self.current_tok.string} was not definded operator"
            )
    def type_65(self, parent): # NEWLINE type (\n)
        return self.type_4(parent)
  
    def make_tree_of_if(self, parent, is_while = False):
        node = Node("if", token = self.current_tok)
        if is_while: node = Node("while", token = self.current_tok)
        condition_node = Node("condition", parent=node, token = None)
        error = self.is_next_match("(")
        if error: return None, error
        
        self.advance()
        while self.current_tok.string != ")":
            temp, error = self.build_ast(condition_node)
            if error: return None, error
            self.advance()
        self.advance()
        while self.current_tok.string == "\n" or self.current_tok.type == 4: self.advance()
        if self.current_tok.string != "{":
            assign_node = Node("assign", parent=node, token = None)
            while True:
                temp, error = self.build_ast(assign_node)
                if error: return None, error
                elif temp.name == 'new_line':
                    self.reverse()
                    break
                self.advance()
            return node, None
        else:
            assign_node, error = self.make_tree_of_assign(node)
            if error: return None, error
            assign_node.parent = node
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
        while self.current_tok.string == "\n" or self.current_tok.type == 4: self.advance()
        if self.current_tok.string != "{":
            node = Node("assign", parent=if_node, token = None)
            while True:
                temp, error = self.build_ast(node)
                if error: return None, error
                elif temp.name == 'new_line':
                    self.reverse()
                    break
                self.advance()
            return if_node, None
        else:
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
            Node(type_, parent=node, token = None)
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
        if self.current_tok.string == "{": self.advance()

        while self.current_tok.string != "}":
            temp, error = self.build_ast(node)
            if error: return None, error
            self.advance()

        return node, None
    def make_tree_of_break(self, parent):
        if parent.name != "assign" or parent.parent.name != "while":
            return None, InvalidSyntaxError(
                self.current_tok,
                self.filename,
                f"Break must be in loop"
            )
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
        tok = self.current_tok
        condition = tok.line[tok.start[1] + 1:]
        # print(tok.start[1])
        # print(condition)
        condition = condition[:condition.find(")")]
        Node(condition, parent=node, token = None)
        if error: return None, error
        paren_cnt = 1
        while paren_cnt > 0:
            self.advance()
            if self.current_tok.string == "(": paren_cnt += 1
            if self.current_tok.string == ")": paren_cnt -= 1
        error = self.is_next_match("{")
        if error: return None, error
        self.make_tree_of_assign(execute_node)
        return execute_node, None

    def operator_basic(self, parent): # 이항연산
        operator = self.current_tok.string
        if operator == ".": operator = "dot"
        node = Node("operator", token = None)
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
        node = None
        if pre_token.type != 1:
            node, error = self.operator_make_array()
            if error: return None, error
            return node, error
        else:
            node, error = self.operator_member(parent)
            if error: return None, error
            return node, error
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
        while self.current_tok.string != "]":
            self.advance()
            if self.current_tok.string == ",": continue
            temp, error = self.build_ast(node)
            if error: return None, error
        return node, error
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
        temp_node = None
        while True:
            tok = self.advance()
            if tok.string == "b":
                Node("bool", parent=temp_node, token = self.current_tok)
                tok = self.advance()
            elif tok.string == "d":
                Node("double", parent=temp_node, token = self.current_tok)
                tok = self.advance()
            elif tok.string == "f":
                Node("float", parent=temp_node, token = self.current_tok)
                tok = self.advance()
            while tok.string == "\n" or tok.string == ",": tok = self.advance()
            if tok.string == "}": break
            elif tok.type != 1:
                return None, InvalidSyntaxError(
                    tok,
                    self.filename,
                    "name type was expected, but it's not"
                )
            temp_node = Node(tok.string, parent=node, token = self.current_tok)
            error = self.is_next_match(":")
            if error: return None, error
            self.advance()
            temp, error = self.build_ast(temp_node)
            if error: return None, error
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
        node = Node("operator", token=None)
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

    def is_next_match(self, target):
        tok = self.advance()
        while tok.string == "\n" or tok.type == 4: tok = self.advance()
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
    def __init__(self, name, type_, is_array, temp = "", details = None) -> None:
        self.name = name
        self.type = type_
        self.is_array = is_array
        self.temp = temp
        self.details = details
        self.value = False
    
    def __str__(self):
        return f"({self.name}, {self.type}, {self.is_array}, {self.temp}, {self.value})"

class Function:
    def __init__(self, name, type_, inputs, temp) -> None:
        self.name = name
        self.type = type_
        self.inputs = inputs
        self.temp = temp

#######################################
# INTERPRETER
#######################################

def make_basic_files(file_dir, namespace = "pack"):
    if os.path.exists(file_dir + f"{namespace}"): shutil.rmtree(file_dir + f"{namespace}")

    os.makedirs(file_dir + f"{namespace}/data/minecraft/tags/functions")
    os.makedirs(file_dir + f"{namespace}/data/{namespace}/functions")

    file = open(file_dir + f"{namespace}/data/minecraft/tags/functions/load.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:load\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/minecraft/tags/functions/tick.json", "w+")
    file.write(f"{{\"values\": [\"{namespace}:tick\"]}}")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/functions/load.mcfunction", "w+")
    file.write(f"\
# This data pack was compiled with the 40planet's compiler.\n\
# https://github.com/alexmonkey05/Datapack-Compiler\n\n")
    file.close()
    file = open(file_dir + f"{namespace}/data/{namespace}/functions/tick.mcfunction", "w+")
    file.close()
    file = open(file_dir + f"{namespace}/pack.mcmeta", "w+")
    file.write('{ "pack": {"pack_format": 9, "description": "by 40planet"} }')
    file.close()

class Interpreter:
    def __init__(self, root, current_dir = "", result_dir = "./", namespace = "pack", filename = "") -> None:
        self.root = root
        self.current_node = root
        self.result_dir = result_dir
        self.filename = filename
        self.namespace = namespace
        self.current_dir = result_dir + f"{self.namespace}/data/{self.namespace}/functions/" + current_dir
        self.current_file = "load.mcfunction"
        # self.variables = { "0":[Variable("0", "int", False, "0")] }
        self.variables = {}
        self.functions = {}
        self.modules = {}

        self.dump_function_cnt = 0
        self.using_variables = [{}]
        self.is_parameter = False

        self.const = []

    def interprete(self, node, current_dir = None, current_file = None):
        if node.name == "root" or node.name == "assign":
            for child in node.children:
                var_name, error = self.interprete(child)
                if error: return None, error
            return None, None
        if current_dir: self.current_dir = current_dir
        if current_file: self.current_file = current_file


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
    def define_function_(self, node): # 나중에 구조 뒤엎기
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
        return None, None
    def call_function_(self, node): # 나중에 구조 뒤엎기
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
                self.write(f"data modify storage {STORAGE_NAME} {var.temp} set from storage {STORAGE_NAME} {temp}\n")
            else:
                self.write(f"data modify storage {STORAGE_NAME} {var.temp} set value {temp}\n")

        file.write(f"function {self.namespace}:{self.get_folder_dir()}{fun.name}\n")
        file.close()
        return fun.temp, None
    def import_(self, node):
        name = node.children[0].name
        try:
            os.makedirs(self.result_dir +f"{self.namespace}/data/{self.namespace}/functions/{name}/")
        except:
            return None, None
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/functions/{name}/load.mcfunction", "w+").close()
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/functions/{name}/tick.mcfunction", "w+").close()
        with open(self.result_dir + f"{self.namespace}/data/minecraft/tags/functions/load.json") as f:
            data = json.load(f)
            data["values"].append(f"{self.namespace}:{name}/load")
            file = open(self.result_dir + f"{self.namespace}/data/minecraft/tags/functions/load.json", "w+")
            file.write(str(data).replace("\'", "\""))
            file.close()
        with open(self.result_dir + f"{self.namespace}/data/minecraft/tags/functions/tick.json") as f:
            data = json.load(f)
            data["values"].append(f"{self.namespace}:{name}/tick")
            file = open(self.result_dir + f"{self.namespace}/data/minecraft/tags/functions/tick.json", "w+")
            file.write(str(data).replace("\'", "\""))
            file.close()
        details, error = interprete("/".join(self.filename.split("/")[:-1]) + "/" + name, self.result_dir, self.namespace, True, node.children[0].token)
        if error: return None, error
        self.variables[name] = [Variable(name, "module", False)]
        self.modules[name] = details
        for fun_name in details["functions"]:
            fun = details["functions"][fun_name]
            self.variables[fun.temp] = [Variable(fun.name, fun.type, False, fun.temp)]
            self.functions[f"{name}.{fun.name}"] = Function(f"{name}/{fun.name}", fun.type, fun.inputs, fun.temp)
        for var_name in details["variables"]:
            var = details["variables"][var_name][0]
            self.variables[var.name] = [var]
        return None, None
    def if_(self, node):
        if_score, error = self.interprete(node.children[0].children[0]) # interprete condition
        if error: return None, error

        current_file = self.current_file
        dump_function = self.make_dump_function()
        self.write(f"execute store result score #{if_score} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {if_score}\nexecute if score #{if_score} {SCOREBOARD_NAME} matches 1 run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
        self.current_file = dump_function
        self.using_variables.append({})

        for child in node.children[1].children:
            temp, error = self.interprete(child) # interprete assign
            if error: return None, error

        self.current_file = current_file

        for var in self.using_variables[-1]:
            used_var_temp.append(self.using_variables[-1][var].temp)
            if var == "0": continue
            self.variables[var].pop(-1)
            if len(self.variables[var]) == 0:
                del(self.variables[var])
        self.using_variables.pop(-1)

        if len(node.children) >= 3:
            
            dump_function = self.make_dump_function()
            self.write(f"execute unless score #{if_score} {SCOREBOARD_NAME} matches 1 run function {self.namespace}:{self.get_folder_dir()}{dump_function[:-11]}\n")
            current_file = self.current_file
            self.current_file = dump_function
            self.using_variables.append({})

            for child in node.children[2].children:
                temp, error = self.interprete(child) # interprete assign
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
        return dump_function, None
    def while_(self, node):
        dump_function, error = self.if_(node)
        if error: return None, error
        current_file = self.current_file
        self.current_file = dump_function

        if_score, error = self.interprete(node.children[0].children[0]) # interprete condition
        if error: return None, error
        self.write(f"execute store result score #{if_score} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {if_score}\nexecute if score #{if_score} {SCOREBOARD_NAME} matches 1 run function {self.namespace}:{self.get_folder_dir()}{self.current_file[:-11]}\n")

        self.current_file = current_file
        return None, None
    def operator_(self, node):
        operator = node.children[0].name
        if operator == "paren":
            return self.operator_(node.children[1])
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
        if "^" in command:
            command, error = self.macro_(command, node.token)
            if error: return None, error
            if command[0] != "$": command = "$" + command
            self.macro(command + "\n")
        else:
            self.write(command + "\n")
        return None, None
    def macro_(self, command, token):
        global used_temp
        while "^" in command:
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
            command = command.replace("^" + var_name + "&", f"$({self.variables[var_name][-1].temp})")
        return command, None
    def make_array_(self, node):
        temp = get_temp()
        self.write(f"data modify storage {STORAGE_NAME} {temp} set value []\n")
        for child in node.children:
            temp2 = child.name
            if temp2 in INTERPRETE_THESE:
                temp2, error = self.interprete(child)
                if error: return None, error
            self.write(f"data modify storage {STORAGE_NAME} {temp} append from storage {STORAGE_NAME} {self.to_storage(temp2)}\n")

        if temp not in self.variables: self.variables[temp] = []
        self.variables[temp].append(Variable(temp, "arr", True, temp))
        return temp, None
    def make_nbt_(self, node):
        temp = get_temp()
        self.write(f"data remove storage {STORAGE_NAME} {temp}\ndata modify storage {STORAGE_NAME} {temp} set value {{}}\n")
        keys = []
        for child in node.children:
            key = child.name
            value = child.children[0].name
            if value in INTERPRETE_THESE:
                value, error = self.interprete(child.children[0])
                if error: return None, error
            # value = value.replace("\"", "\\\"")
            var_temp = self.to_storage(value)
            self.write(f"data modify storage {STORAGE_NAME} {temp}.{key} set from storage {STORAGE_NAME} {var_temp}\n")
            if value in self.variables:
                self.add_var(f"{temp}.{key}", "var_type", self.variables[value][-1].is_array, value)
            else: self.add_var(f"{temp}.{key}", "asdf", False, var_temp)
            keys.append(f"{temp}.{key}")
        self.add_var(temp, "nbt", False, temp, keys)
        return temp, None
    def make_selector_(self, node):
        temp = get_temp()
        command = node.children[0].name
        if "^" in command:
            command = self.macro_(command, node.token)
            self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value \"{command.replace("\"", "\\\"")}\"\n")
        else:
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value \"{command.replace("\"", "\\\"")}\"\n")
        self.add_var(temp, "entity", False, temp)
        return temp, None
    def operator_return(self, node):
        node.children[0].parent = None
        fun_name = self.current_file[:-11]
        temp_node = None
        if fun_name not in self.functions:
            temp_node = node
            while temp_node.name != "define_function":
                temp_node = temp_node.parent
                if temp_node.name == "root":
                    return None, InvalidSyntaxError(
                        temp_node.token,
                        self.filename,
                        f"\"return\" must in function"
                    )
            fun_name = temp_node.children[1].name
        fun = self.functions[fun_name]
        return_node = node.children[0]
        return_value = return_node.name
        if return_value in INTERPRETE_THESE:
            return_value, error = self.interprete(return_node)
            if error: return None, error
        if return_value in self.variables: self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set from storage {STORAGE_NAME} {self.variables[return_value][-1].temp}\nreturn run data get storage {STORAGE_NAME} {fun.temp}")
        else: self.write(f"data modify storage {STORAGE_NAME} {fun.temp} set value {return_value}\nreturn {return_value}")
        return fun.temp, None
    def break_(self, node):
        self.write("return 0\n")
        return None, None
    def execute_(self, node):
        execute = Execute(node.children[0].children[0].name, self, node.token)
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
        for var in self.using_variables[-1]:
            used_var_temp.append(self.using_variables[-1][var].temp)
            if var == "0": continue
            self.variables[var].pop(-1)
            if len(self.variables[var]) == 0:
                del(self.variables[var])
        self.using_variables.pop(-1)


        return None, None


    def operator_equal(self, node):
        var1 = node.children[1].name

        if var1 in INTERPRETE_THESE:
            var1, error = self.interprete(node.children[1])
            if error: return None, error
        if var1.__class__ == Variable:
            var1 = var1.name
        elif var1 in self.const and var1 in self.variables and not self.variables[var1][-1].is_array:
            self.const.remove(var1)


        var2 = node.children[2].name
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
        elif "." in var2:
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
execute store rsult storage {STORAGE_NAME} {temp} byte 1 run scoreboard players operation #{temp1} {SCOREBOARD_NAME} *= #{temp2} {SCOREBOARD_NAME}\n\
")
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        self.add_used_temp(temp1)
        self.add_used_temp(temp2)
        return temp, None
    def operator_member(self, node):
        var_name = node.children[1].name
        if var_name not in self.variables: return None, InvalidSyntaxError(
                node.children[1].token,
                self.filename,
                f"{var_name} is not defined"
            )
        var = self.variables[var_name][-1]
        index = node.children[2].name
        if index in INTERPRETE_THESE:
            index, error = self.interprete(node.children[2])
            if error: return None, error
        temp = get_temp()
        if var_name in self.variables: var_name = self.variables[var_name][-1].temp
        if index in self.variables:
            index = self.variables[index][-1].temp
            self.write(f"\
data modify storage {STORAGE_NAME} var1 set from storage {STORAGE_NAME} {var_name}\n\
data modify storage {STORAGE_NAME} var2 set from storage {STORAGE_NAME} {index}\n\
scoreboard players set #operator_type {SCOREBOARD_NAME} {OPERATOR_ID["member"]}\n\
function basic:operation\n\
data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n\
")
        else:
            self.write(f"\
data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} {var_name}[{index}]\n\
")
        self.add_var(temp, var.type, False, temp)
        self.add_used_temp(index)
        return temp, None
    def operator_not(self, node):
        temp, error = self.interprete(node.children[1])
        if error: return None, error
        self.write(f"execute store result storage {STORAGE_NAME} {temp} byte 1 run data get storage {STORAGE_NAME} {temp}\n")
        self.add_var(temp, "bool", False, temp)
        return temp, None
    def operator_dot(self, node):
        var1_node = node.children[1]
        var2_node = node.children[2]

        var1 = var1_node.name
        if var1 == "operator":
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
                pass
        elif var1 in self.variables: # 인스턴스
            return f"{var1}.{var2}", None
        else: # 모듈 또는 클래스
            
            return None, InvalidSyntaxError(
                var1_node.token,
                self.filename,
                f"{var1} was not definded"
            )

    def fun_print(self, node, input_nodes):
        result_arr = []
        current_file = self.current_file
        dump_file = None
        for input_node in input_nodes:
            temp = input_node.children[0].name
            if temp in INTERPRETE_THESE:
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
        if dump_file: result = "$" + result
        self.write(result)
        if dump_file:
            self.current_file = current_file
            self.write(f"function {self.namespace}:{self.get_folder_dir()}{dump_file[:-11]} with storage {STORAGE_NAME}\n")
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
execute if score #{temp} {SCOREBOARD_NAME} matches 5 run data modify storage {STORAGE_NAME} {temp} set value \"byte\"\n\
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
            var1 = f"$({self.variables[var1][-1].temp})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var2 = f"$({self.variables[var2][-1].temp})"
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
            var1 = f"$({self.variables[var1][-1].temp})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var2 = f"$({self.variables[var2][-1].temp})"
            is_var = True
        elif var2[0] == "\"": var2 = var2[1:-1]
        if var3 in self.variables:
            var3 = f"$({self.variables[var3][-1].temp})"
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
            var1, error = self.interprete(var1)
            if error: return None, error
        var2 = input_nodes[1].children[0].name
        if var2 in INTERPRETE_THESE:
            var2, error = self.interprete(var2)
            if error: return None, error
        var3 = input_nodes[2].children[0].name
        if var3 in INTERPRETE_THESE:
            var3, error = self.interprete(var3)
            if error: return None, error
        
        is_var = False
        if var1 in self.variables:
            is_var = True
            var1 = f"$({self.variables[var1][-1].temp})"
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            is_var = True
            var2 = f"$({self.variables[var2][-1].temp})"
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
            var3, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error
        var4 = input_nodes[3].children[0].name
        if var4 in INTERPRETE_THESE:
            var4, error = self.interprete(input_nodes[1].children[0])
            if error: return None, error

        if var1 not in self.variables and var1 not in ('"entity"', '"block"', '"storage"'):
            return None, InvalidSyntaxError(
                    node.children[0].token,
                    self.filename,
                    f"from parameters must be \"block\", \"entity\" or \"stoage\""
                )
        is_var = False
        if var1 in self.variables:
            var1 = f"$({self.variables[var1][-1].temp})"
            is_var = True
        elif var1[0] == "\"": var1 = var1[1:-1]
        if var2 in self.variables:
            var1 = f"$({self.variables[var2][-1].temp})"
            is_var = True
        elif var2[0] == "\"": var2 = var2[1:-1]
        if var3 in self.variables:
            var3 = f"$({self.variables[var3][-1].temp})"
            is_var = True
        elif var3[0] == "\"": var3 = var3[1:-1]
        if var4 in self.variables:
            if is_var:
                self.macro(f"$data modify {var1} {var2} {var3} set from storage {STORAGE_NAME} {var4}\n")
            else:
                self.write(f"data modify {var1} {var2} {var3} set from storage {STORAGE_NAME} {var4}\n")
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
    def fun_byte(self, node, input_nodes):
        if 1 != len(input_nodes):
            return None, InvalidSyntaxError(
                node.children[0].token,
                self.filename,
                f"byte must have only 1 parameters"
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
    def fun_string(self, node, input_nodes): # 책갈피
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
            self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value \"$({self.variables[var][-1].temp})\"")
        else:
            if var[0] == "\"":
                var = var[1:-1]
            self.write(f"data modify storage {STORAGE_NAME} {temp} set value \"{var}\"")
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
        #     self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value $({self.variables[var][-1].temp})")
        # else:
        #     self.macro(f"$data modify storage {STORAGE_NAME} {temp} set value {var}")
        # self.add_used_temp(var)
        # return temp, None

    def get_folder_dir(self):
        dir_arr = self.current_dir.split("/")
        folder = ""
        dir_arr = dir_arr[dir_arr.index(self.namespace):]
        if len(dir_arr) > 5: folder = "/".join(dir_arr[5:])
        return folder
    
    def to_storage(self, var):
        if var in self.variables:
            return self.variables[var][-1].temp
        temp = get_temp()
        self.write(f"data modify storage {STORAGE_NAME} {temp} set value {var}\n")
        return temp

    def add_used_temp(self, var):
        if var[:4] == "temp":
            used_temp.append(var)
            if var in self.variables: del(self.variables[var])

    def make_dump_function(self):
        filename = str(self.dump_function_cnt) + ".mcfunction"
        self.dump_function_cnt += 1
        file = open(self.current_dir + filename, "w+")
        file.close()
        return filename

    def write(self, txt):
        file = open(self.current_dir + self.current_file, "a", encoding="utf-8")
        file.write(txt)
        file.close()

    def macro(self, txt):
        current_file = self.current_file
        dump_file = self.make_dump_function()
        self.current_file = dump_file
        self.write(txt)
        self.current_file = current_file
        self.write(f"function {self.namespace}:{self.get_folder_dir()}{dump_file[:-11]} with storage {STORAGE_NAME}\n")

    def add_var(self, name, type, is_array, temp, details = None):
        if name not in self.variables: self.variables[name] = []
        self.variables[name].append(Variable(name, type, is_array, temp, details))

class Execute:
    def __init__(self, condition, interpreter, token) -> None:
        self.condition = condition
        self.arr = self.condition.split(" ")
        self.idx = 0
        self.result = "execute "
        self.current_node = self.arr[0]
        self.interpreter = interpreter
        self.len = len(self.arr)
        self.token = token

    def interprete(self):
        while self.len > self.idx:
            if self.current_node == "":
                self.advance()
                if self.len <= self.idx:
                    break
                continue
            method_name = f'execute_{self.current_node}'
            method = getattr(self, method_name)
            error = method()
            if error: return None, error
            self.advance()
        return self.result, None
    
    def advance(self):
        self.idx += 1
        if self.len <= self.idx: return self.current_node
        self.current_node = self.arr[self.idx]
        return self.current_node
    
    def reverse(self):
        self.idx -= 1
        if 0 > self.idx: return self.current_node
        self.current_node = self.arr[self.idx]
        return self.current_node

    def entity(self, node):
        
        result = ""
        
        if node in self.interpreter.variables:
            result = f"$({self.interpreter.variables[node][-1].temp})"
            if self.result[0] != "$": self.result = "$" + self.result
        else:
            result = node
        return result, None
    def position(self):
        pos1 = self.current_node
        pos2 = self.advance()
        pos3 = self.advance()
        if {pos1[0], pos2[0], pos3[0]} == {"^", "~"}:
            return None, InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'"^" and "~" can not be used at once'
            )
        return f"{pos1} {pos2} {pos3}", None
    def set_parameters(self, command, parameters):
        node = self.advance()
        if node not in parameters:
            return InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'\"{command}\" must be followed by one of {parameters}'
            )
        self.result += f"{command} {node} "
    def add_string(self):
        node = self.advance()
        if node[0] == "\"" or node[0] == "'":
            if node[-1] != node[0]:
                return InvalidSyntaxError(
                    self.token,
                    self.interpreter.filename,
                    f'expected {node[0]} but it\'s not. At the end of {node}'
                )
            self.result += f"{node[1:-1]} "
        elif node not in self.interpreter.variables:
            return InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'\"{node}\" is not definded'
            )
        
        else:
            self.result += f"$({self.interpreter.variables[node][-1].temp}) "
            if self.result[0] != "$": self.result = "$" + self.result

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
            return self.set_parameters("positoined", ("world_surface", "motion_blocking", "motion_blocking_no_leaves", "ocean_floor"))
        else:
            position, error = self.position()
            if error: return error
            self.result += f"positioned {position} "
    def execute_align(self):
        return self.set_parameters("align", ("x", "y", "z", "xy", "xz", "yz", "xyz"))
    def execute_facing(self):
        node = self.advance()
        if node == "entity":
            node = self.advance()
            entity, error = self.entity(node)
            if error: return error
            error = self.set_parameters(f"facing entity {entity}", ("eyes", "feet"))
            if error: return error
        else:
            position, error = self.position()
            if error: return error
            self.result += f"facing {position} "
    def execute_rotated(self):
        node = self.advance()
        if node == "as":
            node = self.advance()
            entity, error = self.entity(node)
            if error: return error
            self.result += f"rotated as {entity} "
        else:
            pos1 = self.advance()
            pos2 = self.advance()
            if {pos1[0], pos2[0]} == {"^", "~"}:
                return InvalidSyntaxError(
                    self.token,
                    self.interpreter.filename,
                    f'"^" and "~" can not be used at once'
                )
            self.result += f"rotated {pos1} {pos2}"
    def execute_anchored(self):
        return self.set_parameters("anchored", ("eyes", "feet"))
    def execute_in(self):
        self.result += f"in {self.advance()} "
    def execute_summon(self):
        self.result += f"summon {self.advance()} "
    def execute_on(self):
        return self.set_parameters("on", ("attacker", "controller", "leasher", "origin", "owner", "passengers", "target", "vehicle"))
    def execute_if(self, if_or_unless = "if"):
        error = self.set_parameters(if_or_unless, ("block", "blocks", "entity", "score", "biome", "dimension", "function", "loaded", "predicate", "items"))
        if error: return error
        node = self.current_node
        if node == "block" or node == "biome":
            self.advance()
            pos, error = self.position()
            if error: return error
            self.result += f"{pos} {self.advance()} "
        elif node == "blocks":
            for i in range(3):
                self.advance()
                pos, error = self.position()
                if error: return error
                self.result += f"{pos} "
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
            node = self.advance()
            if node == "matches": self.result += f"matches {self.advance()} "
            elif node in ("<", "<=", "=", ">=", ">"):
                self.result += f"{node} "
                error = self.add_string()
                if error: return error
                error = self.add_string()
                if error: return error
            else:
                return InvalidSyntaxError(
                    self.token,
                    self.interpreter.filename,
                    f'\"<if|unless> score <target> <scoreboard>\" must be followed by one of ("<", "<=", "=", ">=", ">", "matches")'
                )
        elif node == "dimension" or node == "functoin" or node == "predicate":
            self.result += f"{self.advance()} "
        elif node == "loaded":
            self.advance()
            pos, error = self.position()
            if error: return error
            self.result += f"{pos} "
        elif node == "items":
            node = self.advance()
            self.result += node + " "
            if node == "entity":
                entity, error = self.entity(self.advance())
                if error: return error
                self.result += f"{entity} "
            elif node == "block":
                self.advance()
                pos, error = self.position()
                if error: return error
                self.result += f"{pos} "
            else:
                return InvalidSyntaxError(
                    self.token,
                    self.interpreter.filename,
                    f'\"<if|unless> items\" must be followed by one of ("entity", "block")'
                )
            self.result += f"{self.advance()} {self.advance()} "
        else:
            return InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'unexpected Error in execute'
            )
    def execute_unless(self):
        return self.execute_if("unless")
    def execute_store(self):
        error = self.set_parameters("store", ("result", "success"))
        if error: return error
        node = self.advance()
        self.result += node + " "

        if node == "score":
            error = self.add_string()
            if error: return error
            return self.add_string()
        elif node == "block":
            self.advance()
            pos, error = self.position()
            if error: return error
            self.result += f"{pos} {self.advance()}"
            error = self.store_nbt()
            if error: return error
        elif node == "storage":
            self.result += f"{self.advance()} {self.advance()}"
            error = self.store_nbt()
            if error: return error
        elif node == "entity":
            entity, error = self.entity(self.advance())
            if error: return error
            self.result += f"{entity} {self.advance()}"
            error = self.store_nbt()
            if error: return error
        elif node == "bossbar":
            pass
        else:
            return InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'\"store result|success\" must be followed by one of ("score", "block", "storage", "entity", "bossbar")'
            )

    def store_nbt(self):
        
        error = self.set_parameters(f"", MINECRAFT_TYPES)
        if error: return error
        node = self.advance()
        if not node[0].isdigit():
            return InvalidSyntaxError(
                self.token,
                self.interpreter.filename,
                f'\"{node}\" is not decimal'
            )
        self.result += node + " "


temp_cnt = 0
used_temp = []
def get_temp():
    global temp_cnt
    if used_temp.__len__() == 0:
        temp_cnt += 1
        temp = "temp%d" % temp_cnt
    else:
        temp = used_temp.pop()
    return temp

fun_temp_cnt = 0
def get_fun_temp():
    global fun_temp_cnt
    fun_temp_cnt += 1
    temp = "fun_temp%d" % fun_temp_cnt
    return temp

var_temp_cnt = 0
used_var_temp = []
def get_var_temp():
    global var_temp_cnt
    var_temp_cnt += 1
    temp = "var_temp%d" % var_temp_cnt
    return temp


#######################################
# OPTIMIZER
#######################################

class Optimizer:
    def __init__(self, interpreter) -> None:
        self.interpreter = interpreter
    
    def optimize(self):
        self.const_var()
    
    def const_var(self):
        const_arr = []
        
        for var in self.interpreter.const:
            if var.is_array or var.value == False: continue
            if var.value in self.interpreter.variables:
                var.value = self.interpreter.variables[var.value][-1].value
            const_arr.append(var)
        # for var in const_arr:
            # print(var)

def print_tree(ast):
    for pre, fill, node in RenderTree(ast):
        if node.token:
            print("%s%s" % (pre, node.name), end=" | tok: ")
            print(node.token)
        else:
            print("%s%s" % (pre, node.name))

def interprete(filename, result_dir, namespace, is_modul = False, token = None):
    if len(filename) < 7 or filename[-7:] != ".planet": filename += ".planet"
    token_arr = []
    if not os.path.isfile(filename):
        return None, Error(token, f"\"{filename}\" does not exist", filename)
    with tokenize.open(filename) as f:
        tokens = tokenize.generate_tokens(f.readline)
        for token in tokens:
            token_arr.append(token)
    parser = Parser(token_arr, filename)
    ast, error = parser.parse()
    if error:
        if not is_modul: print("\n\n" + error.as_string())
        return None, error
    
    # print_tree(ast)

    interpreter = None
    if not is_modul: interpreter = Interpreter(ast, result_dir=result_dir, namespace=namespace, filename=filename)
    else: interpreter = Interpreter(ast, filename.split("/")[-1][:-7] + "/", result_dir=result_dir, namespace=namespace, filename=filename)
    temp, error = interpreter.interprete(ast)
    if error:
        print("\n\n" + error.as_string())
        return None, error
    
    # optimizer = Optimizer(interpreter)
    # optimizer.optimize()
    return {"variables":interpreter.variables, "functions":interpreter.functions}, None

def generate_datapack(filename, result_dir = "./", namespace = "pack"):
    result_dir = result_dir.strip()
    namespace = namespace.strip()
    if result_dir == "" or namespace == "":
        print("\n\nresult directory and namespace can not be empty string\n")
        return
    if result_dir[-1] != "/" and result_dir[-1] != "\\":
        result_dir += "/"
    make_basic_files(result_dir, namespace)
    return interprete(filename, result_dir, namespace)

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
if __name__ == "__main__":
    # generate_datapack("./example/test.planet", "./", "pack")
    # exit()
    tk = Tk()
    filename = None
    def event():
        namespace = entry1.get().strip()
        if namespace == "": namespace = "pack"
        try:
            name = tk.file.name
            dir = tk.dir
            reset_temp()
            temp, error = generate_datapack(name, dir, namespace)
            if error:
                messagebox.showinfo("name", error.as_string())
            else:
                messagebox.showinfo("name", "done!")
        except:
            pass

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
    btn3 = Button(tk,text='Compile',command=event).grid(row=3,column=0)

    tk.mainloop()