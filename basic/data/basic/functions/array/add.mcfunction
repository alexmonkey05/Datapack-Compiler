execute unless data storage 40planet:value var2[0] run tellraw @a {"text": "Array can only be operated with array","color": "red"}
execute unless data storage 40planet:value var2[0] run return fail

execute store result score #len 40planet_num run data get storage 40planet:value var2
scoreboard players set #idx 40planet_num -1
function basic:array/add/repeat
return run data get storage 40planet:value var1