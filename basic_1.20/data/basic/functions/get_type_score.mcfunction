
execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.int_arr append from storage 40planet:value type_var
execute if score #type 40planet_num matches 1 run data remove storage 40planet:value $type_arr.int_arr[1]
execute if score #type 40planet_num matches 1 run return 1

execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.float_arr append from storage 40planet:value type_var
execute if score #type 40planet_num matches 1 run data remove storage 40planet:value $type_arr.float_arr[1]
execute if score #type 40planet_num matches 1 run return 2

execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.byte_arr append from storage 40planet:value type_var
execute if score #type 40planet_num matches 1 run data remove storage 40planet:value $type_arr.byte_arr[1]
execute if score #type 40planet_num matches 1 run return 5

execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.double_arr append from storage 40planet:value type_var
execute if score #type 40planet_num matches 1 run data remove storage 40planet:value $type_arr.double_arr[1]
execute if score #type 40planet_num matches 1 run return 3

execute store success score #type 40planet_num run data modify storage 40planet:value $type_arr.string_arr append from storage 40planet:value type_var
execute if score #type 40planet_num matches 1 run data remove storage 40planet:value $type_arr.string_arr[1]
execute if score #type 40planet_num matches 1 run return 4

return 0