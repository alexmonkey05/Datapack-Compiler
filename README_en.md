# Datapack-Compiler
This project is a Minecraft datapack compiler.
Developed by **40planet**, free to use as long as proper credit is given.

- [Usage](#usage)
- [VSCode Syntax Highlighting Extension](#vscode-syntax-highlighting-extension)
- [Contributing](#contributing)
- [Grammar](#grammar)
  - [General](#general)
  - [execute](#execute)
  - [import](#import)
  - [Built-in Functions](#built-in-functions)

---

# Usage
~~Video tutorial available here: [Comet Tutorial](https://youtu.be/vzlmWR5MqCY)~~
Currently unavailable — will be re-uploaded soon.

## Installation & Execution
### Using Pre-compiled Binary (Windows only)
1. Download `compiler.exe` from the [Release tab](https://github.com/alexmonkey05/Datapack-Compiler/releases).
2. There are two ways to run it:
   - Run `compiler.exe` directly → GUI mode.
   - Run `compiler.exe --cli <arguments>` → CLI mode.

#### CLI Arguments
| Argument | Description |
| -------- | ----------- |
| `--cli` | Enables CLI mode instead of GUI mode. |
| `-p <planet file>` / `--planet` | Specifies the file to compile. |
| `-v <version>` / `--version` | Minecraft version to compile for. |
| `-d <location>` / `--dist` | Output folder for generated datapack. |
| `-n <namespace>` / `--name` | Namespace name (default=`pack`). |
| `-l` / `--logger` | Sets logging level (default=`INFO`). Levels: `DEBUG` > `INFO` > `WARNING` > `ERROR` > `CRITICAL` > `FATAL` > `LOG`. |
| `-h` / `--help` | Displays help information. |

#### CLI Example
```bash
compiler.exe --cli --planet ./a.planet --version 1.21 --dist ./world/datapacks --name packpack --logger DEBUG
```
```bash
compiler.exe --cli -p ./a.planet -v 1.21 -d ./world/datapacks -n packpack -l DEBUG
```

### Using Project Source Code (Windows, macOS, Linux)
1. Download the source code from the [Release tab](https://github.com/alexmonkey05/Datapack-Compiler/releases).
2. Navigate to the project directory:
   ```bash
   cd <project_path>
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **[Note]** On non-Windows systems, you may need:
   ```bash
   sudo apt-get install python3-tk
   ```
4. Run the compiler:
   ```bash
   python new_compiler.py   # Windows
   python3 new_compiler.py  # macOS/Linux
   ```
   This starts the GUI mode.

---

## GUI Mode
<img src="https://github.com/user-attachments/assets/d4a9549b-1b9f-432b-b3c2-65ea39003410" width=700 /> |  <img src="https://github.com/user-attachments/assets/7207a09f-7ee2-43a6-b353-849a94048805" width=700 />
:----: | :----:
Compilation Success | Compilation Failure

- Namespaces must be lowercase. Default=`pack`.
- Click **Compile** to build the datapack.
- Place the generated datapack and `basic_1.20.zip` or `basic_1.21.zip` inside your Minecraft world's `datapacks` folder.
- For Minecraft `1.21.5+`, the basic datapack will **not** work.
- Enter Minecraft and run `/reload` to apply changes.

---

# VSCode Syntax Highlighting Extension
[Comet Highlighter (VSC Marketplace)](https://marketplace.visualstudio.com/items?itemName=alexmonkey05.comet-highlighter)

You can install it via the link above or by searching **Comet Highlighter** in VSCode Extensions.
**Note:** This extension only provides syntax highlighting — **no autocomplete support**.

---

# Contributing
You can generate an executable using:
```bash
pyinstaller --noconfirm --onefile --console --add-data "<location>\grammer.lark;." --add-data "<location>\web;web/" "<location>\new_compiler.py"
```
# 사용된 라이브러리 목록
```python
import datetime
from lark import Transformer, Token, Tree, Lark
import os
import json
import shutil
import sys
import time
```

---

# Grammar
## General
### Comments
Use `#` to add comments:
```python
# This is an awesome comment!
```

### Data Types
- **int** → `1`, `-2`, `100`
- **float, double** → `1.0`, `3.14`
    - Floats must include `f`, e.g. `1f`, `2.7f`.
- **string** → `"This is string"`
- **nbt** → Similar to JSON, e.g. `{id:"minecraft:block_display",Tags:["temp"]}`

### Variable Declaration
```python
var a
var b = 2.0
var c = "asdf"
var arr = [1, 2, 3]
```

### Local Variables
Variables declared inside blocks are **scoped locally**.
```python
var a
if (condition) {
    var a
}
```

### Newlines & Semicolons
Statements can end with either `\n` or `;`.
```python
var a
var b = {
    test: "asdf"
}

var a;
var b = {
    test: "asdf"
};
```

### Minecraft Commands
Commands starting with `/` are passed directly to Minecraft:
```python
/say hello
/gamemode creative @a
```

### Namespaces: `__namespace__` & `__main__`
- `__namespace__` → Replaced with module path.
- `__main__` → Always replaced with root namespace.

### Macros
Use `$` for macros:
```python
var a = 123
/$say $(a)
var cmd = "say hi"
/$$(cmd)
```

If you type `\$`, it will be changed to `$` when compiling.   
- Wrong example
```
var a = 123
/$say $(a) $
```

```
lark.exceptions.UnexpectedToken: Unexpected token Token('__ANON_21', '$䗻\n') at line 2, column 12.
Expected one of:
        * EOL
        * NO_DOLOR_WORD
        * ESCAPED_DOLOR
        * "$("
        * ESCAPED_MACRO
Previous tokens: [Token('RPAR', ')')]
```
- Correct example
```
var a = 123
/$say $(a) \$
```

```
[@] 123 $
```

In-game macros are also available, although they are a bit complicated.
```
def foo(){
	/$\$say \$(text)
}
/function __namespace__:foo {text:"asdf"}
```

```
[@] asdf
```

### Operators
Order: **Parentheses > Member > Arithmetic > Relational > Logical > Assignment**
- **Arithmetic:** `+`, `-`, `*`, `/`, `%`
- **Relational:** `==`, `!=`, `<=`, `>=`, `<`, `>`
- **Logical:** `and`, `or`, `!`
- **Assignment:** `=`

> ⚠️ **Note:** Arithmetic and relational operators do **not** work in Minecraft `1.21.5+`.

### Conditionals
```python
if(a == 0){
    a = a + 1
} else {
    a = a - 1
}
```
Supports `else if`, but using braces `{}` is recommended to avoid bugs.

### Loops
```python
var a = 0
while(a < 10){
    a = a + 1
}
```
Only `while` and `break` are supported. `for` and `continue` are **not** supported.

### Functions
```python
def tick(){
    var a = 1
}

def test(var a, var b){
    print(a, b)
}
```

Special functions:
- `def tick` → Runs in `#tick`.
- `def load` → Runs in `#load`.

### Function Calls
```python
def hello(){
    print("hi")
}
hello()
```

---

## import
```python
import test

test.print_test()
```

---

## execute
Generally follows Minecraft syntax. Special case:
```python
execute(if function {
    return 1
} positioned 0 0 0){
    print("success!")
}
```

---

## Built-in Functions
| Function | Description |
| -------- | ----------- |
| `print(any ...)` | Prints values to chat. |
| `random()` | Returns a random float between 0 and 1. |
| `type(any)` | Returns the data type as a string. |
| `round(float|double)` | Rounds a number to an integer. |
| `get_score(player, objective)` | Gets a player's scoreboard value. |
| `set_score(player, objective, value)` | Sets a scoreboard value. |
| `get_data(from, name, dir)` | Reads NBT data. |
| `set_data(from, name, dir, value)` | Writes NBT data. |
| `append(arr, elem)` | Appends an element to an array. |
| `del(var)` | Deletes variable or storage data. |
| `len(var)` | Returns length of array or string. |
| `is_module()` | Checks if file is imported as module. |
| `divide(a, b)` | Divides two numbers with 5 decimal precision. |
| `multiply(a, b)` | Multiplies two numbers with 5 decimal precision. |
| `int(a)` | Converts to integer. |
| `float(a)` | Converts to float. |
| `double(a)` | Converts to double. |
| `bool(a)` | Converts to boolean. |
| `string(a)` | Converts to string. |

---

This document is the English version of the project README. For detailed examples and updates, refer to the [official repository](https://github.com/alexmonkey05/Datapack-Compiler).

