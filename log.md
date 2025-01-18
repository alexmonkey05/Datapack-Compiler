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
- `+` 연산자로 원소를 추가할 수 없게 됨
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
- `break`, `return`을 감지하는 명령어가 중복되어 생성되는 오류를 해결함
# 2024/06/17 2.9
- 다차원 배열의 원소에 접근이 불가능하던 오류를 해결함
# 2024/06/22 2.9.1
- `.`연산자를 통해 변수의 요소에 접근 할 때 접근이 안 되던 오류를 해결함
- `README.md`의 몇몇 오타 수정
- `break`, `return`을 판단하는 변수가 초기화가 안 되던 오류를 해결함
- `execute if` 구문에 `data` 추가
# 2024/06/30 2.10
- `del` 내장함수가 삭제된 값을 반환함
- 함수의 인자가 제대로 전달되지 않던 오류를 수정함
- `README.md`에 `del` 내장함수 설명을 적음
- 몇몇 연산에 변수를 넣으면 제대로 작동하지 않던 오류를 해결함
  - `set_data`
  - 멤버연산 `[]`
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
# 2024/08/16 2.12
- `double` 내장함수가 작동하지 않던 오류 수정
- 버전에 `1.21.1` 추가
- 선택한 버전에 따라 `pack.mcmeta`의 버전이 바뀌도록 수정
# 2024/08/23 2.13
- `int`, `float`, `double`끼리의 연산이 가능해짐
- `{}`로 묶인 부분이 파일의 마지막 글자일 때, 무한 로딩이 걸리던 버그를 해결함
# 2024/08/31 2.14
- `if block`이 문법을 제대로 지켜도 에러가 나던 현상을 해결함
- `devide`, `multiply` 추가
- 스토리지에 저장되는 정보에 네임스페이스를 추가함
  - ex) `pack_var_temp10`
- 스토리지에 저장되는 경로가 data 아래로 옮겨짐
- `execute` 구문 내의 모든 좌표는 문자열로 적어야 합니다
```
execute(positioned 0 0 0){...}
```
```
execute(positioned "0 0 0"){...}
```
- `execute` 구문을 한 줄에 적을 필요가 없게 됨
```
execute(as
@a){
  /say a
}
```
- `execute` 구문의 `if function` 성능이 강화됨
```
def test(){
    return 1
}

execute(if function {
    return test()
}){
    print("성공!")
}
```
# 2024/09/24 2.14.1
- `execute if score <플레이어> <스코어보드> matches`의 범위가 제대로 인식되지 않던 오류 수정
- `execute if items`에서 아이템의 아이디 대신 `*`을 넣었을 경우, 에러가 나던 현상 해결
- 함수의 `return`이 제대로 작동하지 않던 오류 해결
- 실행 중 나오는 에러메시지에 `Runtime Error : ` 문구 추가
- nbt와 배열을 생성할 때의 성능 개선
# 2024/09/25 버전업 없음
- `README.md`에 연산자의 자료형에 관한 내용 추가
  - 연산의 결과는 연산자의 뒤쪽 피연산자를 따라갑니다
    - ex) 0.3 * 1 = 0
# 2024/09/30 버전업 없음
- `README`에 `float`와 `double` 자료형의 경우엔 사칙연산에서 소수점 아래 3번째 자리부터 날라간다는 내용 추가
- 몇몇 f format으로 쓰인 부분을 + 연산자로 바꿈
- `README`에 혜성 1강 링크 추가
# 2024/10/01 2.15
- cli 추가 및 `README`에 관련 내용 추가
# 2024/10/02 2.15.1
- `var t = 2.5`와 같이 소수가 대입이 제대로 되지 않던 오류 수정
- `devide` $\to$ `divide` 내장함수 이름 변경
- 2024/10/02 oein님의 풀리퀘 merge
  - 정형화된 CLI 로그 추가
  - 에러 메시지, 실행 시 나오는 아이콘 등
  - 38번째 줄에 있는 `verboseLevel = LOGLEVEL["DEBUG"]`의 `"DEBUG"` 부분을 변경하여 로그에 표시될 내용을 변경할 수 있음
# 2024/10/23 2.16
- 모듈 내의 정의되지 않은 함수를 호출 할 때에 에러메시지가 안 뜨던 오류 수정
- 아래와 같이 `if predicate`를 작성 시, 에러가 나는 현상 수정
```
if predicate {"condition":"minecraft:entity_properties","entity":"this","predicate":{"vehicle":{}}}
```
- 엔티티가 들어갈 자리에 이름을 직접 적거나 UUID를 작성한 경우에 에러를 내던 오류 수정
- import 된 파일에서 다시 import 한 파일의 함수를 호출하는 경우, 호출이 안 되던 오류 수정
- 반복문 안에서 return을 쓸 경우, 함수 탈출이 안 되던 오류 수정
- 아래와 같이 `if block`을 작성 시, 에러가 나는 현상 발견
```
if block "~ ~ ~" chest[facing=east]
```
- `if items`에서 `weapon.offhand` 슬롯을 감지하려고 하면 에러가 나던 현상 수정
- 선택 가능한 버전에 `1.21.2` 추가
# 2024/11/24 2.16.1
- tkinter 모듈의 `Variable`과 혜성의 `Variable`이 충돌하여 에러가 나던 현상 해결
  - `Variable` $\to$ `VariableComet`으로 클래스 명을 바꿔 해결
# 2024/11/26 2.17
- `del(a)`와 같이 del 함수에 변수를 넘겨줬을 경우 data remove 명령어가 제대로 작성되지 않던 오류 해결
- 컴파일 할 때 데이터팩 전체를 지우고 새로 생성하는 것이 아닌, function 폴더만 지우고 새로 생성하는 것으로 바뀜
  - 입력한 네임스페이스 아래의 loot_table, recipe 등을 건드리지 않음
# 2024/11/28
```
var a = @p
print(a)
print(@p)
```
- 위와 같은 코드를 컴파일 하면 두 print의 출력에 차이가 발생하는 문제를 인지함
# 2024/12/27 3.0b
- 포인터 추가
- Lark를 이용해 내부 구조 리마스터
- 이미 정의된 변수를 다시 정의하려 했을 때 에러가 발생하지 않게 됨
- execute의 문법이 다수 개정됨
  - `"~ ~ ~"` $\to$ `~ ~ ~`
  - `if score "@s" "40planet_num"` $\to$ `if score @s 40planet_num`
    - 이 경우엔 전자도 가능하지만, 후자도 가능하도록 바뀜
  - 마인크래프트의 execute 명령어를 그대로 갖다 박아도 무사히 작동되도록 변경함
- 매크로 문법이 변경됨
  - `/say ^variable&` $\to$ `/$say $(variable)`
  - 본래의 마크의 매크로 문법을 살림
- 0b, 1b 등 마크 자료형 문제 해결
- 엔티티 자료형 삭제
### 아직 정식으로 3.0을 릴리즈 한건 아님!
# 2024/12/27
- 늘 그렇듯 if, execute, while에서의 return, break 에러 수정
# 2025/01/01
- 3.0 베타 릴리즈
- `{}`로 nbt를 생성할 때 오류가 나던 현상 해결
- 창모드에서 컴파일이 불가능하던 에러 해결
# 2025/01/06 3.0.1b
- `/$$(a)   $(b)`를 `$(a)$(b)`와 같이 컴파일하던 에러 해결
- 함수의 매개변수로 넘어간 연산을 처리하지 않던 에러 해결
- `multiply` 내장함수가 아예 작동하지 않던 에러 해결
# 2025/01/10 3.0.2b
- pyinstaller로 패키징 했을 때 abspath가 정상작동하지 않아 에러가 나던 현상 해결
- `and`, `or`, `!` 연산 사용 시 에러나던 현상 해결
- 빈 배열(`[]`) 선언 시 에러나던 현상 해결
# 2025/01/13 3.0.3b
- 아래와 같이 배열의 모든 원소에 대해 반복문을 돌리려고 할 때, 무한루프가 발생하는 오류 해결
```
while(arr[0]){
    print(arr[0])
    del(arr[0])
}
```
- while 내부에서 break를 쓰면 while에서까지 break가 동작하는 오류 해결
- 이전 실행의 break의 스코어보드가 이후 실행의 break에 영향을 끼치는 오류 해결
- 대부분의 상황에서 논리연산자가 제대로 작동하지 않던 오류 해결
# 2025/01/18 3.0.4b
- `execute(as @a at @s) /$$(a)`와 같이 "/$"가 맨 처음에 오지 않을 때 매크로가 정상작동하지 않던 오류 해결
- `item.components."minecraft:custom_data"`과 같이 `.`연산에서 문자열을 쓰고자 하면 에러가 나던 현상 해결
- 배열에 음수인덱스 추가
- 아래와 같은 상황에서 문자열을 정상적으로 인식하던 오류 해결
```
a = "as
df"
```
- 매크로를 사용한 커맨드에서 `\$`로 "$"를 입력할 수 있는 기능이 추가됨