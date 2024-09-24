execute unless score #var1_type 40planet_num matches 4 run tellraw @a {"text": "Runtime Error : Operands must be of the same data type","color": "red"}
execute unless score #var1_type 40planet_num matches 4 run return fail

execute if score #operator_type 40planet_num matches 1 run return run function basic:string/add with storage 40planet:value
execute if score #operator_type 40planet_num matches 2..5 run tellraw @a {"text": "Runtime Error : String only can operate \"add\"","color": "red"}
execute if score #operator_type 40planet_num matches 2..5 run return fail
execute if score #operator_type 40planet_num matches 6..7 store success score #var1 40planet_num run data modify storage 40planet:value var1 set from storage 40planet:value var2
execute if score #operator_type 40planet_num matches 6 run return run execute if score #var1 40planet_num matches 0
execute if score #operator_type 40planet_num matches 7 run return run execute if score #var1 40planet_num matches 1
execute if score #operator_type 40planet_num matches 8..11 run tellraw @a {"text": "Runtime Error : String only can operate \"add\"","color": "red"}
execute if score #operator_type 40planet_num matches 8..11 run return fail