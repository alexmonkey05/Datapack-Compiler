

execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.int_arr append from storage 40planet:value var2

execute unless score #type 40planet_num matches 1 run tellraw @a {"text": "Index must be int type","color": "red"}
execute unless score #type 40planet_num matches 1 run return fail

return run function basic:array/member/macro with storage 40planet:value