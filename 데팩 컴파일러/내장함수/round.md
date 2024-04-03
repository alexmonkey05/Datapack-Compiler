```
a = 1.2f
int b = round(a)
```

```
data modify storage 40planet:values a set value 1.2f
execute store result score round num run data get storage 40planet:values a
scoreboard players operation b num = round num
```