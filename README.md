# Datapack-Compiler
## 프로젝트 설명
이 프로젝트는 마인크래프트 컴파일러를 만드는 프로젝트입니다.   
출처(링크)만 표기한다면 자유로운 사용을 허가합니다.

## 문법
### 기본 문법
- 모든 명령어는 함수 안에서 작성되어야 한다. 만약 그렇지 않는다면 에러가 발생한다
```
int a = 1
def test(){
	a = 3
}
```
위의 경우, `int a = 1`이라는 구문이 그 어떠한 함수에도 속해있지 않기 때문에 에러가 발생한다
- `tick`, `load`는 각각 `tick.json`, `load.json`에 들어가는 함수이다
### 자료형 목록
- int
	- `1`, `-2`, `100`과 같은 정수 자료형
- float, double
	- `1.0`, `3.14`와 같은 소수 자료형
- string
	- `"This is string"`과 같은 문자열 자료형
- entity
	- `@a[tag=player]`와 같은 선택인자 자료형
- nbt
	- `{id:"minecraft:block_display",Tags:["temp"]}`와 같은 json 자료형
### 변수 선언
다른 언어와 마찬가지로 `<자료형> <변수명>`의 형태로 선언한다
```
int a
float b = 2.0
entity c = @p[tag=player]
entity d = @p[tag=^b&] # ^b&는 후술할 매크로 기능이다
```

배열 선언은 아래와 같이 `<자료형>[] <변수명>`으로 선언한다
```
int[] array = [1, 2, 3]
float[] array_2
```
만약 선언 이후, 값을 지정해주지 않는다면 각 자료형에 따른 기본값은 아래와 같다
- int - `0`
- float - `0f`
- double - `0d`
- string - `""`
- entity - `""`
- nbt - `{}`
- 모든 배열 - `[]`
	- 아직 발견된 버그는 없으나, 테스트가 부족합니다

### 지역변수
```
int a
if (조건) {
	int a
}
```
이때, if문 안의 a와 밖의 a는 서로 다른 변수이다.   
또한, if문 안에서는 a가 선언 되었으므로 밖의 a에 접근하지 못한다다
### 줄바꿈
`\n` 또는 `;`를 명령어의 끝으로 생각한다
- 단, `[`, `{` 등의 몇몇 예외가 있다
```
int a
nbt b = {
	test: "asdf"
}
```

```
int a;
nbt b = {
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
	- `not`
- 대입
	- `=`
만약 연산의 피연산자들의 자료형이 서로 다른 경우, 에러가 발생한다   
단, `double`과 `float`의 경우엔 에러가 나지 않는다
```
1 + 1.0
```

```
Runtime Error: Diffrent Type
File FILENAME, line 2

    1 + 1.0
      ^
```
### 조건문
`if( <조건> ){ ~~~ }`와 같은 형식으로 작성한다   
~~중괄호를 생략하는 경우, 조건 다음의 명령어 한 줄만 실행한다.~~
```
int a = 0;
if(a == 0){
	a = a + 1;
}
```

```
int a = 0
if(a == 0)
	a = a + 1
```
`if (...) {...} else {...}`과 같은 형태로 else를 사용할 수 있다   
~~마찬가지로 중괄호를 생략하는 경우, 한 줄의 명령어만 실행된다~~
```
int a = 0
if(a == 1){
	a = a + 1
} else {
	a = a - 1
}
```

```
int a = 0
if(a == 1){
	a = a + 1
} else
	a = a - 1
```
~~중괄호를 생략하면 다음 한 줄의 명령어만 실행하기 때문에 `else if` 구문도 지원한다~~
else if를 사용하는 경우 버그가 발생할 수 있으니 되도록 중괄호를 쓰는 것을 권장한다
```
int a = 0
if(a == 1){
	a = a + 1
} else if (a == 0){
	a = a + 2
}
```
### 반복문
`while`의 경우, `if`와 같은 형태로 적을 수 있다
```
int a = 0
while(a < 10){
	a = a + 1
}
```

```
int a = 0
while(a < 10)
	a = a + 1
```
`break` 키워드를 통해 루프를 멈출 수 있다   
`continue`와 `for`는 지원하지 않는다

### 함수 선언
`def [자료형] <함수명>( [매개변수] ){...}`의 형태로 적어 함수를 선언할 수 있다   
`[자료형]`을 생략하면 함수의 반환 자료형은 `void(없음)`으로 설정된다   
`[매개변수]`는 필요에 따라 생략해도 된다   
`[자료형]`을 적었더라도 꼭 값을 반환할 필요는 없다
```
def tick(){
	int a = 1
}
```

```
def int test(int a, float b){
	a = 3
	b = 0.5
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
이때, 매개변수와 인자의 자료형이 다르면 에러가 발생한다
```
def dumb_function(int a){
	return a
}

def load(){
	dumb_function(3)
}
```
### 마인크래프트 명령어
`/`를 맨 앞에 쓰면 그것은 마인크래프트 명령어로 인식한다
```
/say a
/gamemode creative @a
```
   
`^변수명&`처럼 적으면 매크로처럼 사용 가능하다
```
int a = 123
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

test.planet
```
def print_test(){
	print("test")
}
```

main.planet
```
import test
test.print_test()
```

main.planet을 컴파일 했을 때
```
test
```

## execute
1. `if score`를 제외하고는 거의 대부분 마크 문법 그대로 사용해도 된다.
2. `@a[tag=player]`와 같이 선택인자가 들어가는 자리에는 entity 타입의 변수를 넣어도 된다
```
entity player = @a[tag=player]
execute ( as player at @s ){...}
```
### if score
`execute( if score <string name> <string objective> ... )`의 형태로 사용 가능하다

### 주의할 점
문자열을 거의 그대로 넣는 방식이므로 execute에서 버그가 나면 찾기 굉장히 힘들겁니다

## 사용법
### 세팅
1. `compiler.exe`를 받아 실행한다
2. `.planet`파일과 데이터팩이 생성될 폴더를 선택한다
3. 데이터팩의 이름을 입력한다. 
	1. 입력하지 않는다면 `pack`으로 간주한다.
	2. 대문자를 입력하면 데이터팩이 올바르게 작동하지 않는다
4. "변환하기" 버튼을 누른다
5. 마크 안에서 `/reload`를 실행하여 데이터팩을 새로고침해준다

### 기타
- `def tick`을 통해 tick이라는 이름의 함수를 선언한 경우, 이 함수는 매틱 실행된다
- `def load`을 통해 load이라는 이름의 함수를 선언한 경우, 이 함수는 맵이 로딩될 때 1회 실행된다

## 내장함수
### 함수명(자료형 인자, ...)
`함수명`에 관한 설명   
`자료형`이 `any`로 적혀있는 경우, 어떤 자료형이든 상관 없다는 얘기이다.   
`...`이 있는 경우엔 인자가 몇개든 들어갈 수 있다는 것이다
### print(any a1, any a2, ...)
`a1 a2 ...`의 형태로 채팅창에 출력된다
```
int a = 123
print(a)
```

```
123
```
### random()
0~1000 사이의 랜덤한 정수를 반환한다
```
ranadom()
```
### type(any a)
`a`의 자료형을 문자열로 반환한다
```
float test
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
/scorebaord objectives add test dummy
/scoreboard players set asdf test 100
print(get_score("asdf", "test"))
```

```
100
```
### set_score(any var, string player, string objective)
`player`의 `objective`에 `var`의 값을 스코어로 넣는다   
`/scoreboard players set {player} {objective} {var}`와 같은 역할이다
`var`를 반환한다
```
int a = 10
print(set_score(a, "test", "num"))
/tellraw @a {"score":{"name":"test","objective":"num"}}
```

```
10
10
```
### get_data(string from, string|entity name, string dir, string type)
- `from`은 `entity`, `block`, `storage` 중 한가지여야 한다.
- `name`은 블록의 좌표, 저장소의 이름, 엔티티 중 한가지여야 한다
- `dir`은 가져오고자 하는 nbt의 경로를 뜻한다
- `type`은 어떤 자료형으로 읽어오고자 하는지를 뜻한다   
`/data get {from} {name} {dir}`와 같은 역할이다
```
/data modify storage minecraft:test test_dir set value "it's test string!"
print(get_data("storage", "minecraft:test", "test_dir", "string"))
```

```
it's test string!
```
### set_data(string from, string|entity name, string dir, any var)
- `from`은 `entity`, `block`, `storage` 중 한가지여야 한다.
- `name`은 블록의 좌표, 저장소의 이름, 엔티티 중 한가지여야 한다
- `dir`은 가져오고자 하는 nbt의 경로를 뜻한다
- `type`은 어떤 자료형으로 읽어오고자 하는지를 뜻한다   
`/data modify {from} {name} {dir} set value {var}`와 같은 역할이다
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
### doble(any a)
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
### entity(string a)
`a`를 `entity`로 변환해준다   
**아직 불완전하므로 `"@a"`와 같은 변수만 하는 것을 추천합니다**
```
string test = "@s"
entity self = entity(test)
def print_self(){
    print(self)
}
```

```
<실행한 사람의 닉네임>
```
