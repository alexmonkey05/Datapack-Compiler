
```
float a = 1.0
float b = devide(a, 2.0)
```

```
data modify storage 40planet:values a set value 1.0f
data modify storage 40planet:calc list set value [0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f, 0f,0f,0f,0f]
# 변수 셋팅
scoreboard players set #end calc 1
# 변수 -> 리스트
data modify storage 40planet:calc list[0] set from storage 40planet:values a
data modify storage 40planet:calc list[-1] set value 2.0f
# 계산
data modify entity 0-0-0-0-a transformation set from storage 40planet:calc list
data modify storage 40planet:values b set from entity 0-0-0-0-a transformation.scale[0]
