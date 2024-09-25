# Datapack-Compiler
## Project Description
This project is about creating a Minecraft compiler.   
It was created by 40planet, and free use is permitted as long as the link is indicated.

## Highlighter Extension
[Comet Highlighter(VSC Marketplace Link)](https://marketplace.visualstudio.com/items?itemName=alexmonkey05.comet-highlighter)   
You can use the link above or run VSCode and search for Comet Highlighter in extensions to download and use it.   
This extension only displays colors and does not have an auto-completion feature.
## How to use
### Setting
1. Download `compiler.exe` and execute.
2. Select `.planet` file and directory where the data pack will be created
3. Enter the name of the data pack.
	1. If it's blank, it's same as `pack`.
	2. Datapack does not work correctly when entering uppercase letters
4. Press "convert"
5. Put generated datapack ans `basic_1.21.zip` or `basic_1.20` in the `datapacks` folder in saves
6. Refresh the data pack by executing `/reload` in the mark.
7. If you reload your datapack again, go to no.4
## Syntax
### Data types
- int
	- intager like `1`, `-2`, `100`
- float, double
	- decimal like `1.0`, `3.14`
- string
	- string like `"This is string"`
- entity
	- selector like `@a[tag=player]`
- nbt
	- json like `{id:"minecraft:block_display",Tags:["temp"]}`
### Define variable
Declared in the form `var <variable name>`
```
var a
var b = 2.0
var c = @p[tag=player]
var d = @p[tag=^b&] # ^b& is macro
```

Array declarations are declared just like other variables.
```
var array = [1, 2, 3]
```
### Local variable
```
var a
if ( condition ) {
	var a
}
```
At this time, a inside the if statement and a outside the if statement are different variables.   
Also, since a is declared inside the if statement, a outside of it cannot be accessed.
### Line break
Consider `\n` or `;` as the end of a command
- However, there are some exceptions such as `[`, `{`, etc.
```
var a
var b = {
	test: "asdf"
}
```

```
var a;
var b = {
	test: "asdf"
};
```
### Operations
Operations are performed in the following order:   
parenthesis > member > arithmetic > relationship > logic (and, or) > assignment.
- parenthesis
	- `()`
- member(Operations to access elements of an array)
	- `[]`
- arithmetic
	- `+`
	- `-`
	- `*`
	- `/`
	- `%`
- relationship
	- `==`
	- `!=`
	- `<=`
	- `>=`
	- `<`
	- `>`
- logic
	- `and`
	- `or`
	- `!`
- assignment
	- `=`
If the data types of the operands of an operation are different, an error occurs.   
However, in the case of `double` and `float`, no error occurs.
```
1 + 1.0
```

```
Runtime Error: Diffrent Type
File FILENAME, line 2

    1 + 1.0
      ^
```
- The result of an operation follows the last operand.
  - ex) 0.3 * 1 = 0
In the case of `!`, you must put parentheses after it, such as `!(is_module())`.   
In other words, it should be used like a function.
### if / else
Write in the format `if( <condition> ){ ~~~ }`   
If the curly braces are omitted, only one command line following the condition is executed.
```
var a = 0;
if(a == 0){
	a = a + 1;
}
```

```
var a = 0
if(a == 0)
	a = a + 1
```
You can use else in the form `if (...) {...} else {...}`.   
Likewise, if you omit the curly braces, only one line of commands is executed.
```
var a = 0
if(a == 1){
	a = a + 1
} else {
	a = a - 1
}
```

```
var a = 0
if(a == 1){
	a = a + 1
} else
	a = a - 1
```
The `else if` statement is also supported because if the curly braces are omitted, only the next single line of command is executed.   
However, bugs may occur when using else if, so it is recommended to use curly braces whenever possible.
```
var a = 0
if(a == 1){
	a = a + 1
} else if (a == 0){
	a = a + 2
}
```
You can just put a variable in the condition without an operation.   
```
var a = 1
if(a){ # true
	print(a)
}
```
At this time, the standard for judging true/false follows Minecraft's `execute store` syntax.   
Because of this, if the following values ​​are entered, false may be returned.
- "" (empty string)
- 0.4 (decimal number that becomes 0 when rounded)
- -1 (negative number)
- [] (empty array)
### while
In the case of `while`, it can be written in the same form as `if`.
```
var a = 0
while(a < 10){
	a = a + 1
}
```

```
var a = 0
while(a < 10)
	a = a + 1
```
You can stop the loop using the `break` keyword.   
`continue` and `for` are not supported

### Define function
You can declare a function by writing it in the form `def <function name>( [parameter] ){...}`.   
`[parameter]` can be omitted if necessary.
```
def tick(){
	var a = 1
}
```

```
def test(var a, var b){
    print(a, b)
}
```
If you use capital letters in a function name, Minecraft will assume that the function does not exist.   
~~Idiot~~   
So let’s avoid using capital letters in function names.  
   
- If you declare a function named tick through `def tick`, this function is executed as a tick.
- If you declare a function named load through `def load`, this function is executed once when the map is loaded.
- `load` and `tick` executed like this cannot accept arguments.
### Call function
You can call a function by writing it as `function name (argument)`.
```
def wa(var a){
	return "sans"
}

def load(){
	wa(3)
}
```
If you want to call a function using the `/function` command, you can write it as follows:   
At this time, the most recently used argument is used once again.
```
def dumb_function(var a){
	return a
}

/function __namespace__:dumb_function
```
`__namespace__` will be replaced with the namespace entered by the user.
If it was `imported` as a module, `__namespace__` will be changed to the format `namespace:filename/`, so there is no need to worry.
### Minecraft command
If you put `/` at the beginning, it will be recognized as a Minecraft command.
```
/say a
/gamemode creative @a
```
   
You can use like macro when you wrote like `^variable&`
```
var a = 123
/say ^a&
```

```
[@] 123
```

### Comment
You can comment using `#` or `/#`
```
# Comments not written in the data pack
/# Comments written in data pack
```
~~Actually, I was wondering if `/#` was necessary, but I wrote it down first~~

## import
You can import `filename.planet` in the same directory in the form of `import <filename>`.   
`test.planet`
```
def print_test(){
	print("test")
}
```

`main.planet`
```
import test
test.print_test()
```

When compile `main.planet`
```
test
```

## execute
1. Except for `if score`, you can almost always use the mark syntax as is.
2. You can put an entity type variable in place of the selection argument, such as `@a[tag=player]`.
```
var player = @a[tag=player]
execute ( as player at @s ){...}
```
### if score
You can use like `execute( if score <string name> <string objective> ... )`
### if data
- You can use like `if data <변수>`
```
execute(unless data camera_paths[0][1]){
    /scoreboard players set @s 40planet_camera_is_playing 0
}
```
- You can use like `if data <storage|entity|block> <string path>`
```
var id = get_data("entity", "@s", "UUID")
execute(if data storage "temp:test" "id"){
    # code for adding id
}
```
### if function
- If you have defined a function, it can be used in the form of `execute(if function __namespace__:test)`
- It can also be used in the form below without defining a function
```
execute(if function {
    return 1
} positioned "0 0 0"){
    print("success!")
}
```

### Things to note
Since the string is entered almost as is, if there is a bug in execute, it will be very difficult to find.
   

## Built-in function
### Function(type arguments, ...)
Description of `function`   
If `type` is written as `any`, it means that any data type does not matter.   
If there is `...`, any number of arguments can be entered.
### print(any a1, any a2, ...)
It is displayed in the chat window in the form of `a1 a2 ...`
```
var a = 123
print(a)
```

```
123
```
### random()
Returns a random integer between 0 and 1.
```
random()
```
### type(any a)
Returns the type of `a` as a string.
```
var test = 1.0
print(type(test))
```

```
float
```
### round(float|double a)
Rounds the data type `float` or `double` and returns it as `int`.
```
print(round(1.2))
```

```
1
```
### get_score(string player, string objective)
Gets the `objective` score of `player`   
Same as `/scoreboard players get {player} {objective}`
```
/scoreboard objectives add test dummy
/scoreboard players set asdf test 100
print(get_score("asdf", "test"))
```

```
100
```
### set_score(string player, string objective, any var)
Inserts the value of `var` into the `objective` of `player` as the score.   
Same role as `/scoreboard players set {player} {objective} {var}`   
returns `var`
```
var a = 10
print(set_score("test", "num", a))
/tellraw @a {"score":{"name":"test","objective":"num"}}
```

```
10
10
```
### get_data(string from, string|entity name, string dir)
- `from` must be one of `entity`, `block`, or `storage`.
- `name` must be one of block coordinates, storage name, or entity.
- `dir` refers to the path of the nbt you want to import.
Same as `/data get {from} {name} {dir}`.
```
/data modify storage minecraft:test test_dir set value "it's test string!"
print(get_data("storage", "minecraft:test", "test_dir"))
```

```
it's test string!
```
### set_data(string from, string|entity name, string dir, any var)
- `from` must be one of `entity`, `block`, or `storage`.
- `name` must be one of block coordinates, storage name, or entity.
- `dir` refers to the path of the nbt you want to set.
Same as `/data get {from} {name} {dir}`.
```
set_data("storage", "minecraft:test", "test_dir", "it's test string!")
print(get_data("storage", "minecraft:test", "test_dir"))
```
### append(any[] arr, any element)
- `arr` is the array to add elements to.
- `element` is the element to be added
- Same as `/data modify storage 40planet:values ​​{arr} append value {element}`
```
var arr = []
append(arr, 1)
var test = 2
append(arr, test)
print(arr)
```
### del(any var)
- Delete `var` from the repository
- example) `del(arr[1])`
- Same as `/data remove storage 40planet:values ​​{var}`
### len(any var)
- Only accepts array or string types
- Returns the length of `var`
### is_module()
- Determines whether the file has been loaded as a module
- Functions as Python's `__name__ == "__main__"` conditional statement.
```
if(is_module()){
    print("this is not main")
}
```
### devide(int|float|double var, int|float|double var2)
- Calculates `var / var2` to 5 decimal places.
- Return value's type is `float`
```
print(devide(1, 2))
```
### multiply(int|float|double var, int|float|double var2)
- Calculates `var * var2` to 5 decimal places.
- Return value's type is `float`
```
print(multiply(2, 3))
```
### int(any a)
Converts `a` to `int` 자료형으   
`float` 또는 `double`의 경우엔 `round(a)`와 같다
```
print(int(1.2))
print(int("3"))
```

```
1
3
```
### float(any a)
Converts `a` to `float`
```
print(float(1))
```

```
1.0f
```
### double(any a)
Converts `a` to `double`
```
print(double(1))
```

```
1.0d
```
### bool(any a)
Converts `a` to `bool`
```
print(bool(100))
```

```
1
```
### string(any a)
Converts `a` to `string`으
```
print(string(1 + 1))
```

```
2
```
### entity(string a)
Converts `a` to `entity`   
**It is still incomplete, so it is recommended to only use variables like `"@a"`**
```
var test = "@s"
var self = entity(test)
def print_self(){
    print(self)
}
```

```
<Nickname of the person who ran it>
```
