"""Numeric int/float casts for Minecraft 26.3 and later."""

import json
import math

from consts import CNAME, STORAGE_NAME, CometToken, error_as_txt


def compute_conversion(generator, items, target):
    token = items[0]
    arguments = items[1].children if len(items) > 1 else []
    generator.is_parameter_cnt(target, arguments, 1, token)
    argument = arguments[0].children[0]
    value = argument.value
    if argument.type == CNAME:
        generator.is_defined(argument)

    def cast_provider(operand, integer_source):
        if target == "int":
            return operand if integer_source else '{"type":"minecraft:from_float","input":' + operand + '}'
        return '{"type":"minecraft:from_int","input":' + operand + '}' if integer_source else operand

    mode = "integer" if target == "int" else "float"
    result = generator.get_temp()

    def store(provider, prefix=""):
        return f"{prefix}data modify storage {STORAGE_NAME} {result} set compute default {mode} {provider}\n"

    if value in generator.variables:
        commands = argument.command if isinstance(argument, CometToken) else ""
        source = generator.variables[value][-1].temp
        original, integer, comparison, flag = [generator.get_var_temp() for _ in range(4)]
        commands += f"data modify storage {STORAGE_NAME} {original} set from storage {STORAGE_NAME} {source}\n"
        # NBT equality includes the numeric tag type. Comparing with an int copy
        # keeps actual int inputs out of float32 (INT_MAX would otherwise overflow).
        commands += f"execute store result storage {STORAGE_NAME} {integer} int 1 run data get storage {STORAGE_NAME} {original}\n"
        commands += f"data modify storage {STORAGE_NAME} {comparison} set from storage {STORAGE_NAME} {original}\n"
        commands += f"execute store success storage {STORAGE_NAME} {flag} byte 1 run data modify storage {STORAGE_NAME} {comparison} set from storage {STORAGE_NAME} {integer}\n"
        integer_provider = json.dumps({"type": "minecraft:storage", "storage": STORAGE_NAME, "path": integer}, separators=(",", ":"))
        condition = f"data{{{flag.removeprefix('data.')}:0b}}"
        commands += store(cast_provider(integer_provider, True), f"execute if data storage {STORAGE_NAME} {condition} run ")
        # Macro substitution preserves fractions, including numeric strings,
        # without relying on cross-type conversion by the storage provider.
        float_provider = '{"type":"minecraft:constant","value":$(' + original.removeprefix("data.") + ')}'
        commands += store(cast_provider(float_provider, False), f"execute unless data storage {STORAGE_NAME} {condition} run ")
        for path in (original, integer, comparison, flag):
            commands += f"data remove storage {STORAGE_NAME} {path}\n"
    else:
        try:
            raw = json.loads(value) if value.startswith('"') else value
            numeric = float(raw.rstrip("bdf"))
            if not math.isfinite(numeric):
                raise ValueError
            integer_source = (not any(char in raw.lower() for char in ".efd")
                              and numeric.is_integer() and -2147483648 <= numeric <= 2147483647)
        except (ValueError, TypeError, AttributeError):
            raise ValueError(error_as_txt(argument, "InvalidSyntaxError", generator.filename,
                                          f"{target} expects a number or numeric string"))
        operand = json.dumps(int(numeric) if integer_source else numeric)
        commands = store(cast_provider(operand, integer_source))

    generator.add_var(result, result)
    generator.add_used_temp(value)
    return CometToken(target, result, token.start_pos, end_pos=token.end_pos,
                      column=token.column, command=commands, line=token.line)
