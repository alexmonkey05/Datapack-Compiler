### print(변수가 아닌 값, entity entity = @a)
```
print(1)
```

```
tellraw @a "1"
```
---
```
print("ㅁㄴㅇㄹ")
```

```
tellraw @a "ㅁㄴㅇㄹ"
```
### print(int input, entity entity = @a)
- 스코어에 저장하는 자료형
```
int a = 1
entity player = @a[gamemode=!spector]
print(a, player)
```

```
tellraw @a[gamemode=!spector] {"score":{"objective":"num","name":"a"}}
```
### print(double|float|bool input, entity entity = @a)
- 스토리지에 저장하는 자료형
```
float a = 1.0f
entity player = @a[gamemode=!spector]
print(a, player)
```

```
tellraw @a[gamemode=!spector] {"nbt":"a","storage":"40planet:values"}
```
### print(entity input, entity entity = @a, seperator = ", ")
```
entity a = @a
print(a)
```

```
tellraw @a {"selector":"@a"}
```
---
```
entity a = @a
print(a, @a, "|")
```

```
tellraw @a {"selector":"@a","seperator":"|"}
```
