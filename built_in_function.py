from consts import SCORE_TYPES, MINECRAFT_TYPES, TYPES, SCOREBOARD_NAME, STORAGE_NAME, NAMESPACE, DIGITS, INTERPRETE_THESE, BUILT_IN_FUNCTION, OPERATION, OPERATOR_ID, CNAME, INT, ESCAPED_STRING, VariableComet, error_as_txt, Function, CometToken
from transform import CometToken, CNAME, STORAGE_NAME, DatapackGenerater


class BuiltInFunctions(DatapackGenerater):
    def __init__(self, datapack_generator):
        super().__init__(datapack_generator.version, datapack_generator.result_dir, datapack_generator.namespace, datapack_generator.filename, datapack_generator.is_module, datapack_generator.module_name, datapack_generator.visit_tokens)
    
    
    def fun_string(self, node, input_nodes):
        if 1 != len(input_nodes):
            raise ValueError(error_as_txt(
                node.children[0].token,
                "InvalidSyntaxError",
                self.filename,
                f"string must have only 1 parameters"
            ))
        input_node = input_nodes[0].children[0]
        var = input_node.name
        if var in INTERPRETE_THESE:
            var, error = self.interprete(input_node)
            if error: return None, error
        temp = self.get_temp()
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
    