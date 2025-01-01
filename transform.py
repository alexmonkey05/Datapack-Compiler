from lark import Transformer, Token, Lark, Tree
import os
import json

from consts import NEW_LINE, SCORE_TYPES, MINECRAFT_TYPES, TYPES, SCOREBOARD_NAME, STORAGE_NAME, NAMESPACE, BUILT_IN_FUNCTION, OPERATION, OPERATOR_ID, CNAME, INT, ESCAPED_STRING, VariableComet, error_as_txt, Function, CometToken, planet_parser, CometClass


# TODO : 남은거 execute, 내장함수들

#######################################
# DatapackGenerater
#######################################

def modify_file_data(file_data):
    file_lines = file_data.split("\n")
    for i in range(len(file_lines)):
        line = file_lines[i].strip()
        if line[0:2] == "/$":
            file_lines[i] += NEW_LINE
    return "\n".join(file_lines)

imported_files = []
class DatapackGenerater(Transformer):
    def __init__(self, version, result_dir = "./", namespace = "pack", filename = "", is_module = False, module_name = "", visit_tokens = True) -> None:
        super().__init__(visit_tokens)
        # 파라미터 가공
        if type(version) == str: version = float(version[2:])
        self.version = version
        if self.version < 21: self.function_folder = "functions"
        else: self.function_folder = "function"

        # 경로 설정
        self.result_dir = result_dir            # 데이터팩이 생성되는 경로
        self.filename = filename                # 컴파일 할 .planet vkdlf
        self.namespace = namespace              # 네임스페이스
        self.current_dir = result_dir + f"{self.namespace}/data/{self.namespace}/{self.function_folder}/" # 현재 작성중인 .mcfunction 파일이 있는 폴더
        self.module_name = ""
        if is_module:
            self.current_dir += module_name + "/"
            self.module_name = module_name
        self.current_file = "load.mcfunction"   # 현재 작성중인 .mcfunction 파일
        self.is_module = is_module

        # 변수 설정
        self.variables = {
            "false":[VariableComet("false","false")],
            "true":[VariableComet("true","true")]
        }
        self.functions = {}
        self.modules = {}

        # 기타 값 리셋
        self.dump_function_cnt = 0      # n.mcfunction에 쓰일 n
        self.using_variables = [[]]     # 지역변수 스택
        self.is_parameter = False       # 변수 정의할 때 함수의 파라미터로 쓰인 것인지 판단다기 위함
        self.file_content = [""]

        self.const = []
        self.used_return = {}
        self.used_break = []

        # temp 설정
        self.reset_temp()



    def reset_temp(self):
        self.var_temp_cnt = 0
        self.used_var_temp = []
        self.fun_temp_cnt = 0
        self.temp_cnt = 0
        self.used_temp = []
    
    
    def get_temp(self):
        if self.used_temp.__len__() == 0:
            self.temp_cnt += 1
            temp = "data.%s_temp%d" % (self.namespace, self.temp_cnt)
            if self.is_module: temp = "data.%s_%s_temp%d" % (self.namespace, self.module_name, self.temp_cnt)
        else:
            temp = self.used_temp.pop()
        return temp

    def get_fun_temp(self):
        self.fun_temp_cnt += 1
        temp = "data.%s_fun_temp%d" % (self.namespace, self.fun_temp_cnt)
        if self.is_module: temp = "data.%s_%s_fun_temp%d" % (self.namespace, self.module_name, self.fun_temp_cnt)
        return temp

    def get_var_temp(self):
        self.var_temp_cnt += 1
        temp = "data.%s_var_temp%d" % (self.namespace, self.var_temp_cnt)
        if self.is_module: temp = "data.%s_%s_var_temp%d" % (self.namespace, self.module_name, self.var_temp_cnt)
        return temp
    
    # current_dir에서 function 폴더 아래의 경로 가져오기
    # def get_folder_dir(self):
    #     dir_arr = self.current_dir.split("/")
    #     dir_arr = dir_arr[dir_arr.index(self.function_folder):]
    #     folder = "/".join(dir_arr[1:])
    #     return folder

    # var 스토리지에 저장 후 경로 리턴
    def to_storage(self, tok):
        var = tok.value
        result = ""
        if var in self.variables:
            if type(tok) == CometToken: result += tok.command

            if "." not in var[5:] and "[" not in var:
                return self.variables[var][-1].temp, result
            temp = self.get_temp()
            return temp, result + f"data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} {var}\n"
        
        temp = self.get_temp()
        self.add_var(temp, temp)
        if var[0] == "@":
            var = var.replace('"', '\\"')
            return temp, f"data modify storage {STORAGE_NAME} {temp} set value \"{var}\"\n"
        # if tok.type == ESCAPED_STRING:
        #     var = var.replace("\"", "\\\"")
        return temp, f"data modify storage {STORAGE_NAME} {temp} set value {var}\n"

    def add_used_temp(self, var):
        if f"{self.namespace}_temp" in var:
            self.used_temp.append(var)
            if var in self.variables: del(self.variables[var])

    # n.mcfunction 생성
    def make_dump_function(self):
        filename = str(self.dump_function_cnt) + ".mcfunction"
        self.dump_function_cnt += 1
        file = open(self.current_dir + filename, "w+")
        file.close()
        return filename

    def write(self, full_txt):
        txt_arr = full_txt.split("\n")
        # print(txt_arr)
        for txt in txt_arr:
            if len(txt) <= 0: continue
            txt += "\n"
            if txt[0] != "$" and "$(" in txt:
                self.macro(txt)
            else:
                file = open(self.current_dir + self.current_file, "a+", encoding="utf-8")
                file.write(txt)
                file.close()

    def macro(self, txt):
        if txt[0] != "$": txt = "$" + txt
        current_file = self.current_file
        dump_file = self.make_dump_function()
        self.current_file = dump_file
        self.write(txt)
        self.current_file = current_file
        if self.is_module: self.write(f"function {self.namespace}:{self.module_name}/{dump_file[:-11]} with storage {STORAGE_NAME} data\n")
        else: self.write(f"function {self.namespace}:{dump_file[:-11]} with storage {STORAGE_NAME} data\n")

    def add_var(self, name, temp):
        if name not in self.variables: self.variables[name] = []
        self.variables[name].append(VariableComet(name, temp))
        return name
    def remove_var(self, var):
        del(self.variables[var][-1])
        if len(self.variables[var]) <= 0:
            del(self.variables[var])

    # 정의되지 않은 변수라면 에러 raise
    def is_defined(self, tok):
        if tok.value not in self.variables: raise ValueError(error_as_txt(
                tok,
                "InvalidSyntaxError",
                self.filename,
                f"\"{tok.value}\" is not defined",
            ))
    def is_parameter_cnt(self, fun_name, inputs, cnt = 0, tok = None):
        if len(inputs) != cnt: raise ValueError(error_as_txt(
                tok,
                "InvalidSyntaxError",
                self.filename,
                f"{fun_name} expected to get {cnt} parameters, but it give only {len(inputs)} parameters",
            ))
        
    def merge_string(self, str1, str2_tok, end = " "):
        str2 = str2_tok.value
        if str2 in self.variables:
            str2 = self.variables[str2][-1].temp[5:]
            str1 += f"$({str2})"
        elif str2_tok.type == ESCAPED_STRING: str1 += str2[1:-1]
        else: str1 += str2
        str1 += end
        return str1

    # 현재 파일에 내용 추가
    def start(self, items, called_type = "root"):
        for item in items:
            if type(item) == CometToken:
                self.write(item.command)
                # print("command:", item.command)

    # /로 시작하는 커맨드
    def minecraft_command(self, items):
        command = items[0][1:]
        # __namespace__ 바꾸기
        if NAMESPACE in command:
            if self.is_module: command = command.replace(NAMESPACE + ":", f"{self.namespace}:{self.module_name}/")
            command = command.replace(NAMESPACE, f"{self.namespace}")
        return CometToken("command", items[0][1:], items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    # /$로 시작하는 커맨드
    def command_macro(self, items):
        result = ""
        for item in items:
            name = item.data
            if name == "word": result += item.children[0]
            else:
                result += f"$({self.variables[item.children[0].value][-1].temp[5:]})"
                if type(item.children[0]) == CometToken: result = item.children[0].command + result
        # __namespace__ 바꾸기
        if NAMESPACE in result:
            if self.is_module: result = result.replace(NAMESPACE + ":", f"{self.namespace}:{self.module_name}/")
            result = result.replace(NAMESPACE, f"{self.namespace}")
        return CometToken("command", result, items[0].children[0].start_pos, end_pos=items[-1].children[0].end_pos, column=items[0].children[0].column, command=result, line=items[0].children[0].line)

    ##############
    ## function ##
    ##############

    def function_def(self, items):
        name = items[0].value
        if name in self.functions:raise ValueError(error_as_txt(
            items[0],
            "InvalidSyntaxError",
            self.filename,
            f"{name} already defined",
        ))
        function_= Function(name, "function", [], self.get_fun_temp())
        for variable in items[1]:
            # variable = VariableComet(child.value, self.get_var_temp())
            function_.inputs.append(variable)
            self.remove_var(variable.name)
        self.functions[name] = function_

        current_file = self.current_file
        self.current_file = name + ".mcfunction"
        self.write("\n")
        self.start(items[2].children)
        self.current_file = current_file

        # return 쓰인 temp 메모리 풀어주기
        for return_temp in self.used_return:
            self.add_used_temp(return_temp)
        self.used_return = {}
        return Token("function_def", name, items[0].start_pos, items[0].line, items[0].column, items[0].end_line, items[0].end_column, items[0].end_pos)
    # function_def에서 파라미터를 지역변수 리스트(self.variables)에 추가
    def parameter_list(self, items):
        parameters = []
        for child in items:
            variable = VariableComet(child.value, self.get_var_temp())
            parameters.append(variable)
            self.add_var(variable.name, variable.temp)
        return parameters

    def function_call(self, items):
        name = items[0].value
        if name in BUILT_IN_FUNCTION:
            method_name = f'fun_{name}'
            method = getattr(self, method_name)
            return method(items)
        if name not in self.functions: raise ValueError(error_as_txt(
                items[0],
                "InvalidSyntaxError",
                self.filename,
                f"\"{name}\" is not defined",
            ))

        command = ""
        function_ = self.functions[name]
        arguments = items[1].children

        # 주어진 인자 개수와 받을 인자 개수가 맞는지 판단
        # 만약 안 맞다면 에러 던지기
        self.is_parameter_cnt(function_.name, arguments, len(function_.inputs), items[0])

        # 인자 넘겨주는 부분
        for i in range(len(arguments)):
            argument = arguments[i].children[0]
            argument_value = argument.value
            if argument_value in self.variables:
                if type(argument) == CometToken: command += argument.command
                command += f"data modify storage {STORAGE_NAME} {function_.inputs[i].temp} set from storage {STORAGE_NAME} {self.variables[argument_value][-1].temp}\n"
            else:
                command += f"data modify storage {STORAGE_NAME} {function_.inputs[i].temp} set value {argument_value}\n"
        
        if self.is_module:
            command += f"function {self.namespace}:{self.module_name}/{name}\n"
        else:
            command += f"function {self.namespace}:{name}\n"
        return CometToken("function", self.functions[name].temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    
    def fun_print(self, items):
        arguments = items[1]
        result_arr = []
        result = ""
        command = ""
        for argument in arguments.children:
            if type(argument) == CometToken:
                result_arr.append('{"selector":"%s"}' % (argument.command))
                continue

            temp = argument.children[0]

            if type(temp) == CometToken:
                value = temp.value
                command += temp.command
                result_arr.append('{"nbt":"%s","storage":"%s"}' % (self.variables[value][-1].temp, STORAGE_NAME))
                continue

            if temp.value in self.variables:
                result_arr.append('{"nbt":"%s","storage":"%s"}' % (self.variables[temp][-1].temp, STORAGE_NAME))
                self.add_used_temp(temp)
                continue
            
            if temp.type == CNAME: self.is_defined(temp)
            elif temp.type == ESCAPED_STRING:
                temp = temp.value[1:-1]
            else: temp = temp.value
            result_arr.append('{"text":"%s"}' % temp)
            self.add_used_temp(temp)
        for string in result_arr:
            result += string + ",\" \", "
        command += "tellraw @a [" + result[:-6] + "]\n"
        return CometToken("function", "print", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_random(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("random", input_nodes, 0, items[0])
        temp = self.get_temp()
        command = f"execute store result storage {STORAGE_NAME} {temp} float 0.001 run random value 0..1000\n"
        self.add_var(temp, temp)
        return CometToken("random", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_type(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("type", input_nodes, 1, items[0])
        var_name = input_nodes[0].children[0].value
        var_temp, result = self.to_storage(input_nodes[0].children[0])
        temp = self.get_temp()
        result += f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {var_temp}\n\
execute store result score #{temp} {SCOREBOARD_NAME} run function basic:get_type_score\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 0 run data modify storage {STORAGE_NAME} {temp} set value \"nbt\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 1 run data modify storage {STORAGE_NAME} {temp} set value \"int\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 2 run data modify storage {STORAGE_NAME} {temp} set value \"float\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 3 run data modify storage {STORAGE_NAME} {temp} set value \"double\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 4 run data modify storage {STORAGE_NAME} {temp} set value \"string\"\n\
execute if score #{temp} {SCOREBOARD_NAME} matches 5 run data modify storage {STORAGE_NAME} {temp} set value \"bool\"\n\
"
        self.add_var(temp, temp)
        self.add_used_temp(var_name)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result
        return CometToken("type", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_round(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("round", input_nodes, 1, items[0])
        var_name = input_nodes[0].children[0].value
        temp = self.get_temp()
        result = ""
        if var_name in self.variables:
            result += f"execute store result storage {STORAGE_NAME} {temp} int 1 run data get storage {STORAGE_NAME} {self.variables[var_name][-1].temp}\n"
        else:
            try:
                result += f"data modify storage {STORAGE_NAME} {temp} set value {round(float(var_name))}\n"
            except: raise ValueError(error_as_txt(
                input_nodes[0].children[0],
                "InvalidSyntaxError",
                self.filename,
                f"{var_name} is not number"
            ))
        self.add_var(temp, temp)
        self.add_used_temp(var_name)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result
        return CometToken("round", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_get_score(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("get_score", input_nodes, 2, items[0])
        if 2 != len(input_nodes):
            raise ValueError(error_as_txt(
                items[0],
                "InvalidSyntaxError",
                self.filename,
                f"get_score must have only 1 parameters"
            ))
        
        temp = self.get_temp()
        result = f"execute store result storage {STORAGE_NAME} {temp} int 1 run scoreboard players get "
        result = self.merge_string(result, input_nodes[0].children[0])
        result = self.merge_string(result, input_nodes[1].children[0], end="\n")

        self.add_used_temp(input_nodes[0].children[0].value)
        self.add_used_temp(input_nodes[1].children[0].value)
        self.add_var(temp, temp)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result
        return CometToken("get_score", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_set_score(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("set_score", input_nodes, 3, items[0])
        
        value, result = self.to_storage(input_nodes[2].children[0])
        temp = self.get_temp()
        result += f"execute store result score "
        result = self.merge_string(result, input_nodes[0].children[0])
        result = self.merge_string(result, input_nodes[1].children[0], end=f" run data get storage {STORAGE_NAME} {value}\n")

        self.add_used_temp(input_nodes[0].children[0].value)
        self.add_used_temp(input_nodes[1].children[0].value)
        self.add_used_temp(value)
        self.add_var(temp, temp)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result
        return CometToken("get_score", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_get_data(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("get_data", input_nodes, 3, items[0])
        temp = self.get_temp()
        result = f"data modify storage {STORAGE_NAME} {temp} set from "
        result = self.merge_string(result, input_nodes[0].children[0])
        result = self.merge_string(result, input_nodes[1].children[0])
        result = self.merge_string(result, input_nodes[2].children[0], end="\n")

        self.add_used_temp(input_nodes[0].children[0].value)
        self.add_used_temp(input_nodes[1].children[0].value)
        self.add_used_temp(input_nodes[2].children[0].value)
        self.add_var(temp, temp)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result
        return CometToken("get_score", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_set_data(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("set_data", input_nodes, 4, items[0])
        
        value, result = self.to_storage(input_nodes[3].children[0])
        temp = self.get_temp()
        result += f"data modify "
        result = self.merge_string(result, input_nodes[0].children[0])
        result = self.merge_string(result, input_nodes[1].children[0])
        result = self.merge_string(result, input_nodes[2].children[0], end=f" set from storage {STORAGE_NAME} {value}")

        self.add_used_temp(input_nodes[0].children[0].value)
        self.add_used_temp(input_nodes[1].children[0].value)
        self.add_used_temp(input_nodes[2].children[0].value)
        self.add_used_temp(input_nodes[3].children[0].value)
        self.add_used_temp(value)
        self.add_var(temp, temp)

        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: result = input_node.children[0].command + result

        return CometToken("get_score", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    def fun_int(self, items): return self.fun_round(items)
#     def fun_bool(self, items):
        
#         input_nodes = items[1].children
#         self.is_parameter_cnt("bool", input_nodes, 1, items[0])
        
#         input_node = input_nodes[0].children[0]
#         temp, command = self.to_storage(input_node)
#         command += f"execute store result score {SCOREBOARD_NAME} #temp run data get storage {STORAGE_NAME} {temp}\n\
# execute if score #temp {SCOREBOARD_NAME} matches 1.. run data modify storage {STORAGE_NAME} {temp} set value 1b\n\
# execute if score #temp {SCOREBOARD_NAME} matches ..0 run data modify storage {STORAGE_NAME} {temp} set value 0b\n"

#         self.add_used_temp(input_node.value)
#         self.add_var(temp, temp)
#         return CometToken("bool", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_float(self, items, type_ = "float"):
        input_nodes = items[1].children
        self.is_parameter_cnt(type_, input_nodes, 1, items[0])

        command = ""

        input_node = input_nodes[0].children[0]
        if type(input_node) == CometToken: command += input_node.command
        var = input_node.value

        temp = self.get_temp()
        if var in self.variables:
            command += f"data modify storage {STORAGE_NAME} type_var set from storage {STORAGE_NAME} {self.variables[var][-1].temp}\n\
execute store result score #type {SCOREBOARD_NAME} run function basic:get_type_score\n\
function basic:{type_}/convert/execute\n\
data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n"
        elif var[0] == "\"":
            command += f"data modify storage {STORAGE_NAME} {temp} set value {var[1:-1]}{type_[0]}\n"
        elif var[0] == "@":
            raise ValueError(error_as_txt(
                input_node,
                "InvalidSyntaxError",
                self.filename,
                f"\"entity\" can not be \"{type_}\""
            ))
        elif "." in var:
            command += f"data modify storage {STORAGE_NAME} {temp} set value {(float(var))}{type_[0]}\n"
        else:
            command += f"data modify storage {STORAGE_NAME} {temp} set value {var}{type_[0]}\n"

        self.add_used_temp(var)
        self.add_var(temp, temp)
        return CometToken("float", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_double(self, items): return self.fun_float(items, "double")
    def fun_del(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("del", input_nodes, 1, items[0])

        var = input_nodes[0].children[0]
        self.is_defined(var)
        var = var.value

        command = ""
        if type(input_nodes[0].children[0]) == CometToken: command += input_nodes[0].children[0].command

        temp = self.get_temp()
        command += f"data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} {var}\n"
        command += f"data remove storage {STORAGE_NAME} {self.variables[var][-1].temp}\n"
        self.add_var(temp, temp)
        return CometToken("del", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_append(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("append", input_nodes, 2, items[0])

        arr_node = input_nodes[0].children[0]
        arr = arr_node.value
        
        self.is_defined(arr_node)
        arr = self.variables[arr][-1].temp

        command = ""
        if type(arr_node) == CometToken: command += arr_node.command

        element = input_nodes[1].children[0]
        if type(element) == CometToken: command += element.command
        

        if element in self.variables:
            command += f"data modify storage {STORAGE_NAME} {arr} append from storage {STORAGE_NAME} {self.variables[element][-1].temp}\n"
        else:
            command += f"data modify storage {STORAGE_NAME} {arr} append value {element}\n"
        
        return CometToken("append", arr_node.value, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_is_module(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("is_module", input_nodes, 0, items[0])
        temp = self.get_temp()
        self.add_var(temp, temp)
        if self.is_module:
            return CometToken("is_module", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=f"data modify storage {STORAGE_NAME} {temp} set value 1b\n", line=items[0].line)
        return CometToken("is_module", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=f"data modify storage {STORAGE_NAME} {temp} set value 0b\n", line=items[0].line)
    def fun_len(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("len", input_nodes, 1, items[0])
        
        var = input_nodes[0].children[0]
        self.is_defined(var)

        temp = self.get_temp()
        command = f"execute store result storage {STORAGE_NAME} {temp} int 1 run data get storage {STORAGE_NAME} {self.variables[var][-1].temp}\n"
        self.add_var(temp, temp)
        for input_node in input_nodes:
            if type(input_node.children[0]) == CometToken: command = input_node.children[0].command + command
        return CometToken("len", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_divide(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("divide", input_nodes, 2, items[0])

        command = ""

        var = input_nodes[0].children[0]
        if type(var) == CometToken: command += var.command
        var = var.value

        var2 = input_nodes[1].children[0]
        if type(var2) == CometToken: command += var2.command
        var2 = var2.value

        if var in self.variables:
            var = self.variables[var][-1].temp
        else:
            var, to_storage_command = self.to_storage(var)
            command += to_storage_command

        if var2 in self.variables:
            var2 = self.variables[var2][-1].temp
        else:
            var2, to_storage_command = self.to_storage(var2)
            command += to_storage_command

        temp = self.get_temp()
        command += f"data modify storage 40planet:calc list set value [0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f]\n\
execute store result storage 40planet:calc list[0] float 0.00001 run data get storage {STORAGE_NAME} {var} 100000\n\
execute store result storage 40planet:calc list[-1] float 0.00001 run data get storage {STORAGE_NAME} {var2} 100000\n\
data modify entity 0-0-0-0-a transformation set from storage 40planet:calc list\n\
data modify storage {STORAGE_NAME} {temp} set from entity 0-0-0-0-a transformation.scale[0]\n"
        self.add_var(temp, temp)
        return CometToken("divide", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    def fun_multiply(self, items):
        input_nodes = items[1].children
        self.is_parameter_cnt("multiply", input_nodes, 2, items[0])

        command = ""

        var = input_nodes[0].children[0]
        if type(var) == CometToken: command += var.command
        var = var.value

        var2 = input_nodes[1].children[0]
        if type(var2) == CometToken: command += var2.command
        var2 = var2.value

        if var in self.variables:
            var = self.variables[var][-1].temp
        else:
            var, to_storage_command = self.to_storage(var)
            command += to_storage_command

        if var2 in self.variables:
            var2 = self.variables[var2][-1].temp
        else:
            var2, to_storage_command = self.to_storage(var2)
            command += to_storage_command

        temp = self.get_temp()
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
        self.add_var(temp, temp)
        return CometToken("multiply", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)

    
        
    
    

    ##############
    ## operator ##
    ##############

    def operator_basic(self, items, operator):
        result = ""
        var1 = items[0].value
        var2 = items[1].value

        temp = self.get_temp()
        if var1 != "var1":
            if var1 in self.variables:
                if type(items[0]) == CometToken: result += items[0].command
                result += f"data modify storage {STORAGE_NAME} var1 set from storage {STORAGE_NAME} {self.variables[var1][-1].temp}\n"
            elif items[0].type == CNAME: self.is_defined(items[0])
            else: result += f"data modify storage {STORAGE_NAME} var1 set value {var1}\n"
        if var2 in self.variables:
            if type(items[1]) == CometToken: result += items[1].command
            result += f"data modify storage {STORAGE_NAME} var2 set from storage {STORAGE_NAME} {self.variables[var2][-1].temp}\n"
        elif items[1].type == CNAME: self.is_defined(items[1])
        else: result += f"data modify storage {STORAGE_NAME} var2 set value {var2}\n"
        result += f"scoreboard players set #operator_type {SCOREBOARD_NAME} {OPERATOR_ID[operator]}\nfunction basic:operation\ndata modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} var1\n"
        self.add_var(temp, temp)
        self.add_used_temp(var1)
        self.add_used_temp(var2)
        
        return CometToken("operator", temp, items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, command=result, line=items[0].line)
    
    def add(self, items): return self.operator_basic(items, "+")
    def sub(self, items): return self.operator_basic(items, "-")
    def mul(self, items): return self.operator_basic(items, "*")
    def div(self, items): return self.operator_basic(items, "/")
    def mod(self, items): return self.operator_basic(items, "%")
    def equal(self, items): return self.operator_basic(items, "==")
    def not_equal(self, items): return self.operator_basic(items, "!=")
    def bigger_equal(self, items): return self.operator_basic(items, ">=")
    def smaller_equal(self, items): return self.operator_basic(items, "<=")
    def smaller(self, items): return self.operator_basic(items, "<")
    def bigger(self, items): return self.operator_basic(items, ">")
    # def member_operation(self, items): return self.operator_basic(items, "member")

    def neg(self, items):
        variable = items[0]
        if variable.value in self.variables:
            return self.operator_basic([Token("INT", "0", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, line=items[0].line), items[0]], "-")
        return Token("INT", f"-{variable.value}", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, line=items[0].line)

    def dot_operation(self, items):
        var1 = items[0].value
        var2 = items[1].value

        self.is_defined(items[0])
        var1 = self.variables[var1][-1].temp
        self.add_var(f"{var1}.{var2}", f"{var1}.{var2}")
        self.add_used_temp(var1)
        
        if type(items[0]) == CometToken:
            return CometToken(CNAME, f"{var1}.{var2}", items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, line=items[0].line, command=items[0].command)

        return Token(CNAME, f"{var1}.{var2}", items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, line=items[0].line)
    def member_operation(self, items):
        var1 = items[0].value
        var2 = items[1].value
        result = ""

        self.is_defined(items[0])
        var1 = self.variables[var1][-1].temp
        if type(items[0]) == CometToken: result += items[0].command
        if var2 in self.variables:
            if type(items[1]) == CometToken: result += items[1].command
            temp = self.get_temp()
            result += f"data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} {var1}[$({self.variables[var2][-1].temp[5:]})]\n"
            self.add_var(temp, temp)
            return CometToken("operation", temp, items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, command=result, line=items[0].line)
        if items[1].type == CNAME: self.is_defined(items[1])
        self.add_var(f"{var1}[{var2}]", f"{var1}[{var2}]")
        if result == "": return Token(CNAME, f"{var1}[{var2}]", items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, line=items[0].line)
        return CometToken(CNAME, f"{var1}[{var2}]", items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, command=result, line=items[0].line)
    def address(self, items):
        variable = items[0]
        self.is_defined(variable)
        var_address = self.variables[variable.value][-1].temp
        temp = self.get_temp()
        command = ""
        if type(variable) == CometToken: command += variable.command
        command += f"data modify storage {STORAGE_NAME} {temp} set value \"{var_address}\"\n"
        self.add_var(temp, temp)
        self.add_used_temp(variable.value)
        return CometToken("operation", temp, variable.start_pos, end_pos=variable.end_pos, column=variable.column, command=command, line=items[0].line)
    def pointer(self, items):
        variable = items[0]
        self.is_defined(variable)
        temp = self.get_temp()
        command = ""
        # if type(variable) == CometToken: command += variable.command
        storage_value, to_storage_command = self.to_storage(variable)
        command += to_storage_command
        command += f"data modify storage {STORAGE_NAME} {temp} set from storage {STORAGE_NAME} $({storage_value[5:]})\n"
        self.add_var(temp, temp)
        self.add_used_temp(variable.value)
        return CometToken("operation", temp, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)
    
    
    ##############
    ## variable ##
    ##############

    def variable_def(self, items):
        var_name = items[0].value
        # if var_name in self.using_variables[-1]:
        #     raise ValueError(error_as_txt(
        #         items[0],
        #         "InvalidSyntaxError",
        #         self.filename,
        #         f"\"{var_name}\" already defined",
        #     ))
        var_temp = self.get_var_temp()
        self.add_var(var_name, var_temp)
        self.using_variables[-1].append(var_name)
        return Token("variable", var_name, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, line=items[0].line)
    
    def variable_set(self, items):
        variable = items[0].value
        value = items[1].value

        self.is_defined(items[0])
        
        result = ""
        if value in self.variables:
            if type(items[1]) == CometToken: result += items[1].command
            result += f"data modify storage {STORAGE_NAME} {self.variables[variable][-1].temp} set from storage {STORAGE_NAME} {self.variables[value][-1].temp}\n"
        else:
            result += f"data modify storage {STORAGE_NAME} {self.variables[variable][-1].temp} set value {value}\n"
        return CometToken("operation", "set_variable", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=result, line=items[0].line)
    
    def nbt(self, items):
        temp = self.get_temp()
        item_cnt = len(items)
        if item_cnt == 0:
            return CometToken("nbt", temp, command=f"data remove storage {STORAGE_NAME} {temp}\ndata modify storage {STORAGE_NAME} {temp} set value {{}}\n")
        not_include_var = "{"
        is_first = True
        result = f"data remove storage {STORAGE_NAME} {temp}\n"
        for pair in items:
            key = pair.children[0].value
            value = pair.children[1]

            if value.type == CNAME and value.value not in self.variables: raise ValueError(error_as_txt(
                    value,
                    "InvalidSyntaxError",
                    self.filename,
                    f"\"{value.value}\" is not defined"
                ))
            if value.value in self.variables:
                if is_first and len(not_include_var) > 2:
                    result += f"data modify storage {STORAGE_NAME} {temp} set value {not_include_var[:-1]}" + "}\n"
                    is_first = False
                value_temp = self.variables[value.value][-1].temp
                if type(value) == CometToken: result += value.command
                result += f"data modify storage {STORAGE_NAME} {temp}.{key} set from storage {STORAGE_NAME} {value_temp}\n"
                self.add_used_temp(value_temp)
            elif is_first:
                not_include_var += f"{key}:{value.value},"
            else:
                result += f"data modify storage {STORAGE_NAME} {temp}.{key} set value {value.value}\n"
            
        if is_first and len(not_include_var) > 2:
            result += f"data modify storage {STORAGE_NAME} {temp} set value {not_include_var[:-1]}" + "}\n"
        self.add_var(temp, temp)
        return CometToken("nbt", temp, items[0].children[0].start_pos, end_pos=items[0].children[0].end_pos, column=items[0].children[0].column, command=result, line=items[0].children[0].line)

    def array(self, items):
        not_include_var = "["
        is_first = True
        temp = self.get_temp()
        result = ""
        for i in range(len(items)):
            item = items[i]


            if item.type == CNAME and item.value not in self.variables: raise ValueError(error_as_txt(
                    item,
                    "InvalidSyntaxError",
                    self.filename,
                    f"\"{item.value}\" is not defined"
                ))
            
            if type(item) == CometToken: result += item.command

            if item.value in self.variables:
                if is_first and len(not_include_var) > 2:
                    result = f"data modify storage {STORAGE_NAME} {temp} set value {not_include_var[:-1]}]\n" + result
                    is_first = False
                item_temp = self.variables[item.value][-1].temp
                if type(item) == CometToken: result += item.command
                result += f"data modify storage {STORAGE_NAME} {temp} append from storage {STORAGE_NAME} {item_temp}\n"
                self.add_used_temp(item_temp)
            elif is_first:
                not_include_var += f"{item.value},"
            else:
                result += f"data modify storage {STORAGE_NAME} {temp} append value {item.value}\n"
            
        if is_first and len(not_include_var) > 2:
            result = f"data modify storage {STORAGE_NAME} {temp} set value {not_include_var[:-1]}]\n"
        elif is_first: result = f"data modify storage {STORAGE_NAME} {temp} set value []\n" + result
        self.add_var(temp, temp)
        return CometToken("array", temp, items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=result, line=items[0].line)


    ##############
    ##  blocks  ##
    ##############

    def import_statement(self, items):
        name = items[0].value
        if name in imported_files: return None
        imported_files.append(name)

        # 모듈 폴더 생성
        os.makedirs(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/")
        
        # tick. load 함수 생성
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/load.mcfunction", "w+").close()
        open(self.result_dir +f"{self.namespace}/data/{self.namespace}/{self.function_folder}/{name}/tick.mcfunction", "w+").close()
        # #tick, #load에 함수 추가
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
        
        filename = "/".join(self.filename.replace("\\", "/").split("/")[:-1])
        filename += "/" + name + ".planet"
        with open(filename, "r", encoding="utf-8") as file:
            file_data = modify_file_data(file.read())
        parser_tree = planet_parser.parse(file_data + "\n")

        datapack_generator = DatapackGenerater(self.version, self.result_dir, self.namespace, filename, True, name)
        datapack_generator.transform(parser_tree)

        self.variables[name] = [VariableComet(name, "module", False)]
        self.modules[name] = {
            "variables": datapack_generator.variables,
            "functions": datapack_generator.functions
        }
        for fun_name in datapack_generator.functions:
            fun = datapack_generator.functions[fun_name]
            self.variables[fun.temp] = [VariableComet(fun.name, fun.temp)]
            self.functions[f"{name}.{fun.name}"] = Function(f"{name}/{fun.name}", fun.type, fun.inputs, fun.temp)
        for var_name in datapack_generator.variables:
            var = datapack_generator.variables[var_name][0]
            if var_name == var.temp: continue
            self.variables[f"{name}.{var.name}"] = [var]
        
        return None
    
    def if_statement(self, items, is_while = False):
        filename = self.make_dump_function()

        # 조건 판단
        condition, command = self.to_storage(items[0])
        # if type(items[0]) == CometToken: command = items[0].command + command
        if_temp = self.get_temp()
        command += f"execute store result score #{if_temp} {SCOREBOARD_NAME} run data get storage {STORAGE_NAME} {condition}\n"
        # block 실행
        if self.is_module:
            command += f"execute if score #{if_temp} {SCOREBOARD_NAME} matches 1.. run function {self.namespace}:{self.module_name}/{filename[:-11]}\n"
        else:
            command += f"execute if score #{if_temp} {SCOREBOARD_NAME} matches 1.. run function {self.namespace}:{filename[:-11]}\n"

        # while에서 호출한 경우 반복을 위한 구문 추가
        if is_while:
            items[1].children.append(CometToken("while_temp", "asdf", command=command))
        # else 노드 처리
        elif len(items) >= 3:
            else_filename = self.make_dump_function()
            current_file = self.current_file
            self.current_file = else_filename
            self.write("\n")
            self.start(items[2].children)
            self.current_file = current_file
            if self.is_module:
                command += f"execute if score #{if_temp} {SCOREBOARD_NAME} matches ..0 run function {self.namespace}:{self.module_name}/{else_filename[:-11]}\n"
            else:
                command += f"execute if score #{if_temp} {SCOREBOARD_NAME} matches ..0 run function {self.namespace}:{else_filename[:-11]}\n"

        current_file = self.current_file
        self.current_file = filename
        self.write("\n")
        self.start(items[1].children)
        self.current_file = current_file

        for break_temp in self.used_break:
            command += f"execute if score #{break_temp} {SCOREBOARD_NAME} matches 1 run return 0\n"
        for return_temp in self.used_return:
            value = self.used_return[return_temp]
            command += f"execute if score #{return_temp} {SCOREBOARD_NAME} matches 1 run return run data get storage {STORAGE_NAME} {value}\n"

        self.add_used_temp(if_temp)
        return CometToken("operation", "set_variable", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)

    def while_statement(self, items):
        result = self.if_statement(items, True)
        # break에 쓰인 temp 메모리 풀어주기
        for break_temp in self.used_break:
            self.add_used_temp(break_temp)
        self.used_break = []
        
        for temp in self.used_return:
            value = self.used_return[temp]
            result.command += f"execute if score #{temp} {SCOREBOARD_NAME} matches 1 run return run data get storage {STORAGE_NAME} {value}\n"
        
        return result
    
    def break_(self, items):
        temp = self.get_temp()
        self.used_break.append(temp)
        command = f"scoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn 0\n"
        return CometToken("operation", "break", command=command)
    def return_(self, items):
        temp, command = self.to_storage(items[0])
        self.used_return[temp] = temp
        command += f"scoreboard players set #{temp} {SCOREBOARD_NAME} 1\nreturn run data get storage {STORAGE_NAME} {temp}\n"
        return CometToken("operation", "return", items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)


    ##############
    ## execute  ##
    ##############

    def execute(self, items):
        command = "execute "
        for item in items[:-1]:
            command += item.command

        execute_filename = self.make_dump_function()
        current_file = self.current_file
        self.current_file = execute_filename
        self.write("\n")
        self.start(items[-1].children)
        self.current_file = current_file
        if self.is_module: command = f"{command}run function {self.namespace}:{self.module_name}/{execute_filename[:-11]}\n"
        else: command = f"{command}run function {self.namespace}:{execute_filename[:-11]}\n"

        for temp in self.used_return:
            value = self.used_return[temp]
            command += f"execute if score #{temp} {SCOREBOARD_NAME} matches 1 run return run data get storage {STORAGE_NAME} {value}\n"
        for temp in self.used_break:
            command += f"execute if score #{temp} {SCOREBOARD_NAME} matches 1 run return 0\n"

        return CometToken("execute", command, items[0].start_pos, end_pos=items[0].end_pos, column=items[0].column, command=command, line=items[0].line)

    def execute_merge(self, items, seperator = " "):
        command = items[0].value
        if command[-1] != seperator: command += seperator
        if len(items) > 1:
            for item in items[1:]:
                if type(item) == CometToken: command += item.command
                else:
                    command += item.value
                if command[-1] != seperator: command += seperator
        return CometToken("minecraft", command, items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)
    def execute_parameter(self, items): return self.execute_merge(items)
    def coordinate_set(self, items): return self.execute_merge(items)
    def execute_positioned(self, items): return self.execute_merge(items)
    def execute_rotated(self, items): return self.execute_merge(items)
    def execute_facing(self, items): return self.execute_merge(items)
    def execute_store(self, items): return self.execute_merge(items)
    def execute_store_list(self, items): return self.execute_merge(items)
    def nbt_dir(self, items): return self.execute_merge(items, seperator="")
    def execute_if(self, items): return self.execute_merge(items)
    def execute_if_predicate(self, items):
        command = items[0].value
        if len(items) > 1 or "\"" in command:
            command = "{" + command + ","
            for item in items[1:]:
                command += item.command + ","
            command = command[:-1] + "}"
        return CometToken("minecraft", "if_predicate", items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)
    def block_entity(self, items): return self.execute_merge(items)
    def execute_if_data(self, items): return self.execute_merge(items)
    def execute_if_score(self, items): return self.execute_merge(items)
    def execute_if_function(self, items):
        if type(items[0]) == CometToken or type(items[0]) == Token:
            command = items[0].value
            return CometToken("minecraft", "if_function", items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)

        execute_filename = self.make_dump_function()
        current_file = self.current_file
        self.current_file = execute_filename
        self.write("\n")
        self.start(items[-1].children)
        self.current_file = current_file
        if self.is_module: command = f"{self.namespace}:{self.module_name}/{execute_filename[:-11]}"
        else: command = f"{self.namespace}:{execute_filename[:-11]}"

        self.used_return = {}

        return CometToken("execute_if", command, command=command)

    def item(self, items): return self.execute_merge(items, seperator="")
    

    def selector(self, items):
        command = items[0].value
        if len(items) > 1:
            command += "["
            for item in items[1:]:
                command += item.command + ","
            command = command[:-1] + "]"
        return CometToken("minecraft", "selector", items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)

    def selector_parameter(self, items):
        return self.execute_merge(items, seperator="")
    def scores(self, items):
        command = "scores={"
        for i in range(int(len(items) / 2)):
            i *= 2
            command += f"{items[i].value}={items[i+1].value},"
        command = command[:-1] + "}"
        return CometToken("minecraft", "scores_selector", items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)
    def selelctor_nbt(self, items):
        pass

    def json_pair(self, items):
        command = f"{items[0].value}:{items[1].value}"
        return CometToken("minecraft", command, items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)
    def json_(self, items):
        command = "{" + items[0].value + "}"
        return CometToken("minecraft", command, items[0].start_pos, end_pos=items[-1].end_pos, column=items[0].column, command=command, line=items[0].line)
    
    def minecraft_id(self, items):
        if len(items) == 1:
            return items[0]
        namespace = items[0].value
        if namespace == NAMESPACE: namespace = self.namespace
        return Token("minecraft_id", f"{namespace}:{items[1].value}", items[0].start_pos, items[0].line, items[0].column, items[-1].end_line, items[-1].end_column, items[-1].end_pos)
    
    def scoreboard(self, items):
        player = items[0]
        scoreboard = items[1]
        result = ""

        if player.type == ESCAPED_STRING: result += player[1:-1]
        elif player.value in self.variables: result += f"$({self.variables[player.value][-1].temp[5:]})"
        else: result += player
        result += " "
        if scoreboard.type == ESCAPED_STRING: result += scoreboard[1:-1]
        elif scoreboard.value in self.variables: result += f"$({self.variables[scoreboard.value][-1].temp[5:]})"
        else: result += scoreboard
        
        return Token("scoreboard", result, player.start_pos, player.line, player.column, scoreboard.end_line, scoreboard.end_column, scoreboard.end_pos)

    ##############
    ##  class   ##
    ##############

    def class_def(self, items):
        name = items[0].value

        for item in items[1:]:
            print(item, type(item), item.type)
    
    def method(self, items):
        variable = items[0]

        if variable.type == CNAME:
            if variable.value not in self.variables: raise ValueError(error_as_txt(
                variable,
                "InvalidSyntaxError",
                self.filename,
                f"\"{variable.value}\" is not definded",
            ))

            # 변수.함수()
            if variable.value not in self.modules: raise ValueError(error_as_txt(
                variable,
                "InvalidSyntaxError",
                self.filename,
                f"call method of \"{variable.value}\" is not implemented",
            ))

            # 파일명.함수()
            command = ""
            arguments = items[2].children
            name = items[1].value
            functions = self.modules[variable.value]["functions"]
            if name not in functions: raise ValueError(error_as_txt(
                items[1],
                "InvalidSyntaxError",
                self.filename,
                f"\"{name}\" is not defined",
            ))
            function_ = functions[name]
            # 인자 넘겨주는 부분
            for i in range(len(arguments)):
                argument = arguments[i].children[0]
                argument_value = argument.value
                if argument_value in self.variables:
                    if type(argument) == CometToken: command += argument.command
                    command += f"data modify storage {STORAGE_NAME} {function_.inputs[i].temp} set from storage {STORAGE_NAME} {self.variables[argument_value][-1].temp}\n"
                else:
                    command += f"data modify storage {STORAGE_NAME} {function_.inputs[i].temp} set value {argument_value}\n"
            
            command += f"function {self.namespace}:{variable.value}/{name}\n"
            return CometToken("minecraft", function_.temp, items[0].start_pos, end_pos=items[1].end_pos, column=items[0].column, command=command, line=items[0].line)
