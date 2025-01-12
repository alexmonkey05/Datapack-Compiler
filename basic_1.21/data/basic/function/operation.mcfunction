
execute if data storage 40planet:value var1[0] run return run function basic:array/execute
execute unless data storage 40planet:value var1[0] if data storage 40planet:value var2[0] run tellraw @a {"text": "Runtime Error : Array can only be operated with array","color": "red"}
execute unless data storage 40planet:value var1[0] if data storage 40planet:value var2[0] run return fail

data modify storage 40planet:value type_var set from storage 40planet:value var1
execute store result score #var1_type 40planet_num run function basic:get_type_score

# execute if score #var1_type 40planet_num matches 0 if score #operator_type 40planet_num matches 14 run return run function 

execute if score #var1_type 40planet_num matches 0 run tellraw @a {"text": "Runtime Error : nbt type can not be operated","color": "red"}
execute if score #var1_type 40planet_num matches 0 run return fail

execute if score #operator_type 40planet_num matches 12 store result score #var1 40planet_num run data get storage 40planet:value var1
execute if score #operator_type 40planet_num matches 12 run return run execute unless score #var1 40planet_num matches 0

data modify storage 40planet:value type_var set from storage 40planet:value var2
execute store result score #var2_type 40planet_num run function basic:get_type_score
execute if score #var2_type 40planet_num matches 0 run tellraw @a {"text": "Runtime Error : nbt type can not be operated","color": "red"}
execute if score #var2_type 40planet_num matches 0 run return fail

execute if score #var2_type 40planet_num matches 1 store result storage 40planet:value var1 int 1 run return run function basic:int/execute
execute if score #var2_type 40planet_num matches 2 store result storage 40planet:value var1 float 0.01 run return run function basic:float/execute
execute if score #var2_type 40planet_num matches 3 store result storage 40planet:value var1 double 0.01 run return run function basic:double/execute
execute if score #var2_type 40planet_num matches 4 run return run function basic:string/execute
execute if score #var2_type 40planet_num matches 5 store result storage 40planet:value var1 byte 1 run return run function basic:byte/execute

# execute if score #var1_type 40planet_num matches 2..3 run return run data get storage 40planet:value var1 100
# return run data get storage 40planet:value var1