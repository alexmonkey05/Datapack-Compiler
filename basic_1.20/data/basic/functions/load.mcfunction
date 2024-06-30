# This data pack was compiled with the 40planet's compiler.
# https://github.com/alexmonkey05/Datapack-Interpreter
scoreboard objectives add 40planet_num dummy
scoreboard players set 100 40planet_num 100
scoreboard players set #0 40planet_num 0
kill 0-0-0-0-a
summon text_display 0 0 0 {UUID:[I;0,0,0,10]}
forceload add 0 0
data remove storage 40planet:value $type_arr
data modify storage 40planet:value $type_arr set value {int_arr:[1], float_arr:[1f], double_arr:[1d], string_arr:["1"], byte_arr:[1b]}
data modify storage 40planet:value false set value 0b
data modify storage 40planet:value true set value 1b
say done!
