# Datapack-Compiler
이 프로젝트는 마인크래프트 컴파일러를 만드는 프로젝트입니다.   
40행성(40planet)에 의해 제작되었으며, 출처만 표기한다면 자유로운 사용을 허가합니다.   
   
Check english README.md in [here](https://github.com/alexmonkey05/Datapack-Compiler/blob/main/README_en.md)!

 - [사용법](#사용법)
 - [Vscode 문법 강조 확장](#vscode-문법-강조-확장)
 - [기여](#기여)
 - [문법](#문법)
  - [일반](#일반)
	- [execute](#execute)
	- [import](#import)
	- [내장 함수](#내장-함수)

# 사용법
영상 튜토리얼이 있습니다! [Comet Tutorial](https://youtu.be/vzlmWR5MqCY)을 참고하세요.

## 설치 및 실행
### 컴파일 버전 사용 (Windows 한정)
1. [Release 탭](https://github.com/alexmonkey05/Datapack-Compiler/releases)에서 `compiler.exe`를 다운로드합니다.
1. 실행에는 두 가지 방법이 있습니다. `compiler.exe`를 실행할 경우, GUI 모드로 진입하며, `compiler.exe --cli <argument>`를 입력해 실행할 경우, CLI 모드로 진입합니다.

#### 인자 (CLI 모드)
| 인자 | 설명 |
| ---- | ---- |
| `--cli` | GUI 모드 대신 CLI 모드를 사용합니다. |
| `-p <planet file>` or `--planet` | 컴파일 할 파일을 지정합니다. |
| `-v <version>` or `--version` | 컴파일에 사용할 마인크래프트 버전을 지정합니다. |
| `-d <location>` or `--dist` | 결과물이 위치할 폴더를 지정합니다. |
| `-n <namespace>` or `--name` | 네임스페이스를 입력합니다. (기본값=`pack`) |
| `-h` or `--help` | 도움말 페이지를 표시합니다. |

#### 예제 (CLI 모드)
```
compiler.exe --cli --planet ./a.planet --version 1.21 --dist ./world/datapacks --name packpack
```
```
compiler.exe --cli -p ./a.planet -v 1.21 -d ./world/datapacks -n packpack
```

### 프로젝트 코드 사용 (Windows, macOS, Linux)
1. [Release 탭](https://github.com/alexmonkey05/Datapack-Compiler/releases)에서 프로젝트 코드를 다운로드합니다.
1. `cd <프로젝트 경로>`를 실행합니다.
1. `pip install -r requirements.txt`를 실행합니다. 이 작업은 필요한 패키지를 자동으로 설치합니다.\
**[Warning]** 만약, Windows 유저가 아닐경우, `sudo apt-get install python3-tk` 명령어를 입력해야 할 수도 있습니다.
1. `python new_compiler.py`(Windows) 또는 `python3 new_compiler.py`(유니버설)를 실행합니다. 실행 시 GUI 모드로 진입합니다.

## GUI 모드
<img src="https://github.com/user-attachments/assets/d4a9549b-1b9f-432b-b3c2-65ea39003410" width=700 /> |  <img src="https://github.com/user-attachments/assets/7207a09f-7ee2-43a6-b353-849a94048805" width=700 />
:----: | :----:
 컴파일 성공 시 | 컴파일 실패 시

 - 네임스페이스는 소문자만 입력받습니다. 기본값은 `pack`입니다.
 - `컴파일` 버튼을 눌러 코드를 컴파일합니다.
 - 마인크래프트 세이브파일의 `datapacks` 폴더에 생성된 데이터팩과 `basic_1.20.zip` 또는 `basic_1.21.zip`을 넣어줍니다.
 - 이제 마인크래프트에 접속해 `/reload`를 실행해 데이터팩을 새로고침하면 실행됩니다.

# Vscode 문법 강조 확장
[Comet Highlighter(VSC Marketplace Link)](https://marketplace.visualstudio.com/items?itemName=alexmonkey05.comet-highlighter)   
위의 링크로 들어가거나 VSCode를 실행 후 extensions에서 Comet Highlighter를 검색해 다운로드 하여 사용할 수 있습니다   
해당 익스텐션은 색만 표시해줄 뿐, 자동완성 기능은 없습니다

# 기여
 - exe 파일을 이 명령어를 통해 생성할 수 있습니다.
```
pyinstaller --noconfirm --onefile --console --add-data "<location>\grammer.lark;." --add-data "<location>\web;web/" "<location>\new_compiler.py"
```

# 문법
## 일반
### 자료형 목록
- int
	- `1`, `-2`, `100`과 같은 정수 자료형
- float, double
	- `1.0`, `3.14`와 같은 소수 자료형
- string
	- `"This is string"`과 같은 문자열 자료형
- nbt
	- `{id:"minecraft:block_display",Tags:["temp"]}`와 같은 json 자료형
### 변수 선언
`var <변수명>`의 형태로 선언한다
```
var a
var b = 2.0
var c = @p[tag=player]
var d = @p[tag=^b&] # ^b&는 후술할 매크로 기능이다
```

배열 선언은 다른 변수와 똑같이 선언한다
```
var array = [1, 2, 3]
```
### 지역변수
```
var a
if (조건) {
	var a
}
```
이때, if문 안의 a와 밖의 a는 서로 다른 변수이다.   
또한, if문 안에서는 a가 선언 되었으므로 밖의 a에 접근하지 못한다
### 줄바꿈
`\n` 또는 `;`를 명령어의 끝으로 생각한다
- 단, `[`, `{` 등의 몇몇 예외가 있다
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
### 연산
괄호 > 멤버 > 산술 > 관계(부등식) > 논리(and, or) > 대입 순으로 연산이 진행된다
- 괄호
	- `()`
- 멤버(배열의 원소에 접근하는 연산)
	- `[]`
- 산술
	- `+`
	- `-`
	- `*`
	- `/`
	- `%`
	- `double`과 `float`의 경우, 소수점 아래 2자리까지만 값이 보존된다. 더 정확한 값을 얻고 싶다면 `divide`와 `multiply` 함수를 사용하는 것이 좋다.
- 관계
	- `==`
	- `!=`
	- `<=`
	- `>=`
	- `<`
	- `>`
- 논리
	- `and`
	- `or`
	- `!`
- 대입
	- `=`
만약 연산의 피연산자들의 자료형이 서로 다른 경우, 에러가 발생한다   
단, `double`과 `float`, `int`의 경우엔 에러가 나지 않는다
```
1 + "1"
```

```
Runtime Error: Operand must have same type
```
연산의 결과는 연산자의 뒤쪽 피연산자를 따라갑니다   
ex) 0.3 * 1 = 0      
`!`의 경우, `!(is_module())`와 같이 뒤에 괄호를 넣어야 한다   
달리 말하자면 함수처럼 써야 한다는 소리이다
### 조건문
`if( <조건> ){ ~~~ }`와 같은 형식으로 작성한다   
중괄호를 생략하는 경우, 조건 다음의 명령어 한 줄만 실행한다.
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
`if (...) {...} else {...}`과 같은 형태로 else를 사용할 수 있다   
마찬가지로 중괄호를 생략하는 경우, 한 줄의 명령어만 실행된다
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
중괄호를 생략하면 다음 한 줄의 명령어만 실행하기 때문에 `else if` 구문도 지원한다   
그러나 종종 else if를 사용하는 경우 버그가 발생할 수 있으니 되도록 중괄호를 쓰는 것을 권장한다
```
var a = 0
if(a == 1){
	a = a + 1
} else if (a == 0){
	a = a + 2
}
```
조건 안에 연산 없이 변수만 넣어도 된다   
```
var a = 1
if(a){ # true
	print(a)
}
```
이때, 참/거짓을 판단하는 기준은 마인크래프트의 `execute store` 구문을 따른다   
때문애 다음과 같은 값이 들어가는 경우, 거짓이 나올 수 있다
- "" (빈 문자열)
- 0.4 (반올림 했을 때 0이 되는 소수)
- -1 (음수)
- [] (빈 배열)
### 반복문
`while`의 경우, `if`와 같은 형태로 적을 수 있다
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
`break` 키워드를 통해 루프를 멈출 수 있다   
`continue`와 `for`는 지원하지 않는다

### 함수 선언
`def <함수명>( [매개변수] ){...}`의 형태로 적어 함수를 선언할 수 있다   
`[매개변수]`는 필요에 따라 생략해도 된다   
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
함수 이름에 대문자를 사용하면 마인크래프트는 그 함수를 그냥 없는 것으로 생각한다   
~~멍청이이다~~   
그러니 함수명에 대문자를 쓰지 않도록 하자   
   
- `def tick`을 통해 tick이라는 이름의 함수를 선언한 경우, 이 함수는 매틱 실행된다
- `def load`을 통해 load이라는 이름의 함수를 선언한 경우, 이 함수는 맵이 로딩될 때 1회 실행된다
- 이렇게 실행되는 `load`와 `tick`은 인수를 받을 수 없다
### 함수 호출
`함수명(인자)`와 같이 작성하여 함수를 호출 할 수 있다
```
def wa(var a){
	return "sans"
}

def load(){
	wa(3)
}
```
만약 `/function`명령어를 사용해 함수를 호출하고 싶다면 아래와 같이 쓰면 된다   
이때, 인자는 가장 최근에 사용된 인자를 한번 더 사용한다
```
def dumb_function(var a){
	return a
}

/function __namespace__:dumb_function
```
`__namespace__`는 사용자가 입력한 네임스페이스로 바뀐다   
만약 모듈로서 `import` 되었다면 `__namespace__`는 `namespace:filename/`의 형식으로 바뀌므로 걱정할 필요 없다
### 마인크래프트 명령어
`/`를 맨 앞에 쓰면 그것은 마인크래프트 명령어로 인식한다
```
/say a
/gamemode creative @a
```
   
`^변수명&`처럼 적으면 매크로처럼 사용 가능하다
```
var a = 123
/say ^a&
```

```
[@] 123
```

### 주석
`#` 또는 `/#`을 사용해 주석을 달 수 있다
```
# 데이터팩에 적히지 않는 주석
/# 데이터팩에 적히는 주석
```
~~사실 `/#`이 필요할까 하긴 싶은데 일단 적어봤습니다~~

## import
`import <파일명>`의 형태로 같은 디렉토리에 있는 `파일명.planet`을 가져올 수 있다.

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

`main.planet`을 컴파일 했을 때
```
test
```

## execute
1. `if function`을 제외하고는 거의 대부분 마크 문법 그대로 사용해도 된다.
### if function
- 함수를 정의했다면 `execute(if function __namespace__:test)`의 형태로 사용 가능하다
- 함수를 정의하지 않고 아래와 같은 형태로도 사용 가능하다
```
execute(if function {
    return 1
} positioned 0 0 0){
    print("성공!")
}
```
   

## 내장 함수
### 함수명(자료형 인자, ...)
`함수명`에 관한 설명   
`자료형`이 `any`로 적혀있는 경우, 어떤 자료형이든 상관 없다는 얘기이다.   
`...`이 있는 경우엔 인자가 몇개든 들어갈 수 있다는 것이다
### print(any a1, any a2, ...)
`a1 a2 ...`의 형태로 채팅창에 출력된다
```
var a = 123
print(a)
```

```
123
```
### random()
0~1 사이의 랜덤한 정수를 반환한다
```
random()
```
### type(any a)
`a`의 자료형을 문자열로 반환한다
```
var test = 1.0
print(type(test))
```

```
float
```
### round(float|double a)
`float` 또는 `double` 자료형을 반올림하여 `int`로 반환한다
```
print(round(1.2))
```

```
1
```
### get_score(string player, string objective)
`player`의 `objective` 점수를 가져온다   
`/scoreboard players get {player} {objective}`와 같은 역할이다
```
/scoreboard objectives add test dummy
/scoreboard players set asdf test 100
print(get_score("asdf", "test"))
```

```
100
```
### set_score(string player, string objective, any var)
`player`의 `objective`에 `var`의 값을 스코어로 넣는다   
`/scoreboard players set {player} {objective} {var}`와 같은 역할이다   
`var`를 반환한다
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
- `from`은 `entity`, `block`, `storage` 중 한가지여야 한다.
- `name`은 블록의 좌표, 저장소의 이름, 엔티티 중 한가지여야 한다
- `dir`은 가져오고자 하는 nbt의 경로를 뜻한다
`/data get {from} {name} {dir}`와 같은 역할이다
```
/data modify storage minecraft:test test_dir set value "it's test string!"
print(get_data("storage", "minecraft:test", "test_dir"))
```

```
it's test string!
```
### set_data(string from, string|entity name, string dir, any var)
- `from`은 `entity`, `block`, `storage` 중 한가지여야 한다.
- `name`은 블록의 좌표, 저장소의 이름, 엔티티 중 한가지여야 한다
- `dir`은 설정하고자 하는 nbt의 경로를 뜻한다
`/data modify {from} {name} {dir} set value {var}`와 같은 역할이다
```
set_data("storage", "minecraft:test", "test_dir", "it's test string!")
print(get_data("storage", "minecraft:test", "test_dir"))
```
### append(any[] arr, any element)
- `arr`은 원소를 추가할 배열이다.
- `element`는 추가할 원소이다
` `/data modify storage 40planet:values {arr} append value {element}`와 같은 역할이다
```
var arr = []
append(arr, 1)
var test = 2
append(arr, test)
print(arr)
```
### del(any var)
- 저장소에서 `var`을 지웁니다
- 예) `del(arr[1])`
- `/data remove storage 40planet:values {var}`와 같은 역할이다
### len(any var)
- 배열 또는 string 타입만 받습니다
- `var`의 길이를 반환합니다
### is_module()
- 해당 파일이 모듈로써 불러와진 것인지 판단해준다
- 파이썬의 `__name__ == "__main__"` 조건문 역할을 해준다.
```
if(is_module()){
    print("this is not main")
}
```
### divide(int|float|double var, int|float|double var2)
- `var / var2`를 소수점 아래 5자리까지 계산해준다
- 반환값의 타입은 `float`이다
```
print(divide(1, 2))
```
### multiply(int|float|double var, int|float|double var2)
- `var * var2`를 소수점 아래 5자리까지 계산해준다
- 반환값의 타입은 `float`이다
```
print(multiply(2, 3))
```
### int(any a)
`a`를 `int` 자료형으로 변환해준다   
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
`a`를 `float`로 변환해준다
```
print(float(1))
```

```
1.0f
```
### double(any a)
`a`를 `double`로 변환해준다
```
print(double(1))
```

```
1.0d
```
### bool(any a)
`a`를 `bool`로 변환해준다
```
print(bool(100))
```

```
1
```
### string(any a)
`a`를 `string`으로 변환해준다
```
print(string(1 + 1))
```

```
2
```
