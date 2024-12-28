phase_prompt: str = """
[상황]
고객의 요청: "{task}"
현재까지 진행된 단계: 고객 요청에 따라 추가할 기능 설정
현재 진행해야 하는 단계: 추가할 기능에 따른 클래스, 메서드 설정과 그것에 따른 디렉토리 구조 작성
결정된 기능:
{demand_analysis_result}

[지시] 기능을 구현하기 위한 디렉토리 구조를 고려하여 작성하세요.

[조건]
1. 필요한 파일과 클래스, 메서드를 시스템 안정성과 확장성을 고려하여 작성해야 함.
2. 결정된 기능이 전부 포함되어야 함.
3. 궁극적으로 프로젝트가 실행 될 엔트리 포인트인 "main.py"가 있어야 함.
    이후 단계에서 코드 구현 시 테스트 파일들이 추가될 "test/" 디렉토리가 __init__.py만 있어야 함.

답변 형식은 다음과 같은 계층 구조 예시를 따르세요.
작성되는 파일은 전부 최상위 디렉토리 내에 있어야 합니다.
"{return_type_violation_in_inital_structure}"

계층 구조 예시:
```
1. top_level_dir/
    1.1 */
        1.1.1 *.py: description
        ...
    1.2 */
        1.2.1 *.py: description
        ...
    1.3 */
        1.3.1 *.py: description
        ...
    ...
    1.n test/
        1.n.1 __init__.py
    1.n+1 main.py: project main entry point
```


"""
assistant_role_name: str = "System_Architect"
assistant_role_prompt: str = """이번 고객의 요청한 요구 사항은 \"{task}\"입니다.
당신은 고급 시스템 구조 설계 전문가로서, 결정된 기능을 깊이 이해하고 이를 디렉토리 구조와 파일 구성에 자연스럽게 녹여내어 최적의 형태로 설계합니다.
프로젝트의 안정성과 확장성을 자연스럽게 고려하며, 요구 사항에 맞춘 최적의 구조를 마련하는 데 뛰어난 감각을 발휘합니다."""