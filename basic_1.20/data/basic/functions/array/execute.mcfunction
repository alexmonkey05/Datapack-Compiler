execute if score #operator_type 40planet_num matches 2..11 run tellraw @a {"text": "Runtime Error : Array only can operate \"add\"","color": "red"}
execute if score #operator_type 40planet_num matches 2..11 run return fail

execute if score #operator_type 40planet_num matches 1 run return run function basic:array/add

execute if score #operator_type 40planet_num matches 12 store result score #temp 40planet_num run data get storage 40planet:value var1
execute if score #operator_type 40planet_num matches 12 run return run execute unless score #temp 40planet_num matches 0

execute if score #operator_type 40planet_num matches 13 run return run function basic:array/member/execute