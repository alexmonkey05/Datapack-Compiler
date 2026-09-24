"""Numeric built-ins backed by Minecraft 26.3 context number providers."""

import json
import math

from consts import CNAME, COMPUTE_FUNCTIONS, STORAGE_NAME, CometToken, error_as_txt


def compute_function(generator, items):
    token = items[0]
    name = token.value

    def fail(message, error="InvalidSyntaxError", location=token):
        raise ValueError(error_as_txt(location, error, generator.filename, message))

    if generator.version < 260300:
        fail(f"{name} requires Minecraft 26.3 or later", "VersionError")
    mode, fields = COMPUTE_FUNCTIONS[name]
    arguments = [node.children[0] for node in items[1].children] if len(items) > 1 else []
    variadic = fields == ("inputs",)
    if variadic:
        if not arguments:
            fail(f"{name} expected at least 1 parameter")
    else:
        generator.is_parameter_cnt(name, arguments, len(fields), token)

    commands = ""
    operands = []
    snapshots = []
    consumed = []
    for index, argument in enumerate(arguments):
        value = argument.value
        if argument.type == CNAME:
            generator.is_defined(argument)
        if value in generator.variables:
            if isinstance(argument, CometToken):
                commands += argument.command
            path = generator.variables[value][-1].temp
            snapshot = generator.get_var_temp()
            # A macro accepts the original numeric value without data-get rounding
            # or undefined cross-type storage-provider conversion. Capture it before
            # the next argument can call a function that overwrites its source.
            commands += f"data modify storage {STORAGE_NAME} {snapshot} set from storage {STORAGE_NAME} {path}\n"
            snapshots.append(snapshot)
            operands.append(f"$(%s)" % snapshot.removeprefix("data."))
            consumed.append(value)
        else:
            try:
                numeric = float(value.rstrip("bdf"))
                if not math.isfinite(numeric):
                    raise ValueError
            except (ValueError, AttributeError):
                fail(f"{name} expects numeric arguments", location=argument)
            integer_input = mode == "integer" and not (name == "binomial" and index == 1)
            if integer_input:
                if not numeric.is_integer() or not -2147483648 <= numeric <= 2147483647:
                    fail(f"{name} expects a 32-bit integer for {fields[index]}", location=argument)
                numeric = int(numeric)
            operands.append(json.dumps(numeric))

    if variadic:
        body = '"inputs":[' + ",".join(operands) + "]"
    else:
        body = ",".join(json.dumps(field) + ":" + value for field, value in zip(fields, operands))
    provider = '{"type":"minecraft:' + name + '",' + body + "}"
    temp = generator.get_temp()
    commands += f"data modify storage {STORAGE_NAME} {temp} set compute default {mode} {provider}\n"
    for snapshot in snapshots:
        commands += f"data remove storage {STORAGE_NAME} {snapshot}\n"
    generator.add_var(temp, temp)
    for value in dict.fromkeys(consumed):
        generator.add_used_temp(value)
    return CometToken("function", temp, token.start_pos, end_pos=token.end_pos,
                      column=token.column, command=commands, line=token.line)
