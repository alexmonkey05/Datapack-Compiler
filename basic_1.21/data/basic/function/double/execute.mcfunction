
execute unless score #var1_type 40planet_num matches 3 run tellraw @a {"text": "Operands must be of the same data type","color": "red"}
execute unless score #var1_type 40planet_num matches 3 run return fail

execute store result score #var1 40planet_num run data get storage 40planet:value var1 100
execute store result score #var2 40planet_num run data get storage 40planet:value var2 100

execute if score #operator_type 40planet_num matches 1 run return run scoreboard players operation #var1 40planet_num += #var2 40planet_num
execute if score #operator_type 40planet_num matches 2 run return run scoreboard players operation #var1 40planet_num -= #var2 40planet_num
execute if score #operator_type 40planet_num matches 3 run return run scoreboard players operation #var1 40planet_num *= #var2 40planet_num
execute if score #operator_type 40planet_num matches 3 run scoreboard players operation #var1 40planet_num /= 100 40planet_num
execute if score #operator_type 40planet_num matches 4 run scoreboard players operation #var1 40planet_num *= 100 40planet_num
execute if score #operator_type 40planet_num matches 4 run return run scoreboard players operation #var1 40planet_num /= #var2 40planet_num
execute if score #operator_type 40planet_num matches 5 run return run scoreboard players operation #var1 40planet_num %= #var2 40planet_num
execute if score #operator_type 40planet_num matches 6 run return run execute if score #var1 40planet_num = #var2 40planet_num
execute if score #operator_type 40planet_num matches 7 run return run execute unless score #var1 40planet_num = #var2 40planet_num
execute if score #operator_type 40planet_num matches 8 run return run execute if score #var1 40planet_num >= #var2 40planet_num
execute if score #operator_type 40planet_num matches 9 run return run execute if score #var1 40planet_num > #var2 40planet_num
execute if score #operator_type 40planet_num matches 10 run return run execute if score #var1 40planet_num <= #var2 40planet_num
execute if score #operator_type 40planet_num matches 11 run return run execute if score #var1 40planet_num < #var2 40planet_num