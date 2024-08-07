# 2024/05/15 1.0
- 릴리즈
# 2024/05/20 1.1   
- 한글이 깨지는 것 버그 고침
- print에서 지역변수가 인식되던 버그 고침
# 2024/05/31 2.0
- 자료형이 더욱 유동적으로 변함
  - 변수 선언 키워드 변경
	  - ("int", "float", "double", "string", "entity") -> var
  - 함수의 리턴 자료형 설정 불가능
- get_data의 4번째 인자가 삭제됨
  - 3개의 인자만 받도록 변경됨
# 2024/06/03 2.1
- float(a)가 "data modify storage 40planet:value <temp> 1 set value a"로 컴파일 되던 오류 수정
- A가 B를 import하고 B가 A를 import 했을 때 에러나는 현상 오류 수정
# 2024/06/05 2.2
- 버전 선택 기능 추가
# 2024/06/06 2.3
- 아래와 같은 상황에서 break, return이 정상작동 하지 않던 문제를 해결함
```
def test(){
  execute(as @a){
    return 0
  }
  print("return dosen't worked")
}
```
# 2024/06/12 2.4
- 아래와 같은 상황에서 break, return이 정상작동 하지 않던 문제를 해결함
```
def test(){
    if(1 == 1){
        if(1 == 1){
            return 1
            print("asdf")
        }
    }
}
```
- 이중배열 선언 시 오류가 나던 문제를 해결함
- `test.asdf.fdsa`와 같이 "." 연산자로 2번 이상 데이터 접근 시 오류가 나던 문제를 해결함
# 2024/06/13 2.5
- 함수를 정의하고 안에 아무것도 적지 않았을 경우 에러가 나던 문제를 해결함
- `+` 연산으로 배열에 원소를 추가할 수 있음
```
var arr = []
arr = arr + 1
```
- del 내장함수 추가
- basic 데이터팩이 일부 변경 됨
# 2024/06/15 2.6
- 1.20 버전에서 `execute(if items)` 구문을 쓰면 에러가 나도록 바뀜
- 1.21 버전을 선택할 수 있음
# 2024/06/15 2.6.1
- 1.20.4 버전에서 `execute(if items)` 구문을 쓰면 에러가 나도록 바뀜
- 1.20.4, 1.20.6, 1.21 버전을 선택할 수 있음
# 2024/06/15 2.6.2
- `basic.zip` 내의 `functions` 폴더 명이 `function`로 수정됨
- `basic.zip`이 버전에 따라 달라짐에 따라 `basic_1.20.zip`, `basic_1.21.zip`으로 나뉨
- 내장함수 `string`에 변수를 넣었을 경우에 데이터팩에 오류가 나던 현상이 해결됨
# 2024/06/15 2.7
- `__namespace__`를 활용하여 마크 명령어를 입력할 때에 네임스페이스를 쓸 수 있게 됨
```
def dumb_function(var a){
	return a
}

/function __namespace__:dumb_function
```
# 2024/06/16 2.8
- `append` 내장함수가 추가됨
`append(arr, element)`
```
var arr = []
append(arr, 1)
var test = 2
append(arr, test)
print(arr)
```
```
[1, 2]
```
- `string` 내장함수가 제대로 작동하지 않던 오류를 해결함
- `1.20.6`을 선택했을 때에 폴더명이 `function`으로 생성되던 오류를 해결함
# 2024/06/17 2.8.1
- `is_module()` 내장함수 추가
```
if(is_module()){
    print("this is not main")
}
```
- `!` 안에 함수가 들어간 경우 에러가 나던 오류를 해결함
- `!` 연산이 실질적으로 아무것도 수행하지 않던 오류를 해결함
# 2024/06/17 2.8.2
- 모듈 내의 변수에 접근할 수 없던 오류를 해결함
- `break`, `return을` 감지하는 명령어가 중복되어 생성되는 오류를 해결함
# 2024/06/17 2.9
- 다차원 배열의 원소에 접근이 불가능하던 오류를 해결함
# 2024/06/22 2.9.1
- `.`연산자를 통해 변수의 요소에 접근 할 때 접근이 안 되던 오류를 해결함
- `README.md`의 몇몇 오타 수정
- `break`, `return을` 판단하는 변수가 초기화가 안 되던 오류를 해결함
- `execute if` 구문에 `data` 추가
# 2024/06/30 2.10
- `del` 내장함수가 삭제된 값을 반환함
- 함수의 인자가 제대로 전달되지 않던 오류를 수정함
- `README.md`에 `del` 내장함수 설명을 적음
- 몇몇 연산에 변수를 넣으면 제대로 작동하지 않던 오류를 해결함
  -`set_data`
  -멤버연산 `[]`
- `false`, `true` 추가
- `len` 추가
# 2024/07/10 2.10.1
- `README.md` 영어로 변경
- `README_kr.md` 추가
- `README.md`의 `random` 내용 변경
# 2024/07/16 2.10.2
- `execute( if data var )` 형식에서 var에 점 연산이 있을 경우 에러가 나던 문제를 해결함
- nbt 자료형의 키값에 문자열을 넣으면 에러가 나던 문제를 해결함
- `3b`와 같은 `byte` 자료형을 `3`으로 컴파일 하던 에러를 해결함
- print에 선택인자를 넣어도 선택된 엔티티가 출력되지 않던 에러를 해결함
- `basic`의 논리 연산에서 값이 이상하게 나오던 에러를 해결함
- 변수를 실행시키려 할 때, 에러가 나지 않던 것을 해결함
```
var a = 1
a()
```
# 2024/07/16 2.11
- 조건에 연산을 쓰지 않고 `while(var)`, `if(var)`의 형태로 적는 것이 가능해짐
- `README.md`에 관련 내용 추가
# 2024/07/17
- `Comet Highlighter` 익스텐션 업데이트
  - `true`, `false` 키워드 추가
  - `unless` 키워드 추가
# 2024/07/17 2.11.1
- `break`를 사용했을 때 데이터팩이 고장나던 오류 수정
- `while`의 조건에 변수를 넣었을 떼 2 이상인 경우에 반복이 안 되던 오류 수정
- `return`이 2개 이상 있을 때 오류가 나던 현상 해결
- `float`의 곱셈에서 수가 100배가 되던 현상 해결
- `-`연산이 코드에 들어갈 경우 프로그램이 멈추던 오류 해결
# 2024/07/23 2.11.2
- 아래와 같이 `nbt`의 `value` 부분에 연산자 또는 배열을 넣을 경우 에러가 나던 현상 해결
```
var test = {
    arr: [1, 2, 3],
    temp: 1b
}
var test2 = {
    test_arr: test.arr
}
```
- `.` 연산 이후에 멤버 접근 연산을 수행하려 할 때 에러가 나던 현상 해결
```
var laundry = {
    arr: [1, 2, 3],
    temp: 1b
}

print(laundry.arr[0])
print(laundry.arr[0].test)
```
# 2024/08/05 2.11.3
- `README`의 `execute if data` 부분의 오류 수정
```
execute(if data storage "temp:test" id){
```
```
execute(if data storage "temp:test" "id"){
```
- nbt를 만들 때 빈 값(`{}`)이 들어가면 에러가 나던 현상 해결
- nbt를 만들 때 `,`가 없을 때의 에러메시지 수정
```
Invalid Syntax: : was not defined operator
```
```
Invalid Syntax: prior "," is missing
```
# 2024/08/08 2.11.4
- `if`, `else` 등을 중괄호 없이 적었을 때 제대로 인식이 안 되던 오류 수정
```
if(num == 1)
    print(1)
else if(num == 2)
    print(2)
else if(num == 3)
    print(3)
else
    print("예측 실패")
```