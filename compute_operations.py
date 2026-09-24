"""Minecraft 26.3 integer arithmetic command generation."""

import json

from consts import CNAME, STORAGE_NAME, CometToken


def compute_operator(generator, items, operator):
    commands = ""
    operands = []
    paths = []
    for item in items:
        if item.type == CNAME:
            generator.is_defined(item)
        path, setup = generator.to_storage(item)
        commands += setup
        # Capture each operand before the next expression can change its storage.
        snapshot = generator.get_temp()
        commands += (
            f"execute store result storage {STORAGE_NAME} {snapshot} int 1 "
            f"run data get storage {STORAGE_NAME} {path}\n"
        )
        paths.extend([path, snapshot])
        operands.append({"type": "minecraft:storage", "storage": STORAGE_NAME, "path": snapshot})

    # Scoreboard division/modulo floor negative values instead of truncating to zero.
    provider = {"type": "minecraft:" + {
        "+": "add", "-": "sub", "*": "mul", "/": "floor_div", "%": "floor_mod",
    }[operator]}
    if operator in ("+", "*"):
        provider["inputs"] = operands
    else:
        provider.update(left=operands[0], right=operands[1])
    temp = generator.get_temp()
    commands += (
        f"data modify storage {STORAGE_NAME} {temp} set compute default integer "
        f"{json.dumps(provider, separators=(',', ':'))}\n"
    )
    generator.add_var(temp, temp)
    for path in dict.fromkeys(paths + [item.value for item in items]):
        generator.add_used_temp(path)
    return CometToken("operator", temp, items[0].start_pos,
                      end_pos=items[1].end_pos, column=items[0].column,
                      command=commands, line=items[0].line)
