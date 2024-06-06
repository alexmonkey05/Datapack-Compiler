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
