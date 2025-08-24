# This data pack was compiled with the 40planet's compiler.
# https://github.com/alexmonkey05/Datapack-Compiler

scoreboard objectives add 40planet_num dummy
data modify storage 40planet:value data.asdf_temp13 set value [{},{},{},{},{},{},{},{},{},{},{},{}]
data modify storage 40planet:value data.asdf_var_temp1 set from storage 40planet:value data.asdf_temp13
execute store result storage 40planet:value data.asdf_temp14 int 1 run scoreboard players get #x slot_num
execute store result storage 40planet:value data.asdf_temp15 int 1 run scoreboard players get #y slot_num
data modify storage 40planet:value data.asdf_temp16 set from entity @s item
function asdf:0 with storage 40planet:value data
say asdf
