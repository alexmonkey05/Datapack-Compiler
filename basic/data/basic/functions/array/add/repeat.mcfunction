execute store result storage 40planet:value idx int 1 run scoreboard players add #idx 40planet_num 1

function basic:array/add/macro with storage 40planet:value

execute if score #idx 40planet_num < #len 40planet_num run function basic:array/add/repeat