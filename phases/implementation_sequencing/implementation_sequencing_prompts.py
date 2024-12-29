phase_prompt: str = """
[이번 고객의 요청 사항] {task}
[상황]
우리는 작성된 스켈레톤 코드와 프로젝트 구조를 확인하고,
**의존성**을 고려하여 **파일 별** 구현 작업의 우선순위를 작성해야 합니다.
[조건]
1. 스켈레톤 코드에서 파일의 level은 #으로 구별되어 있습니다. 프로젝트 구조를 참고하세요.
2. 작성된 스켈레톤 코드에 포함된 파일만 구현 단계에 포함할 수 있습니다.
3. 구현 단계에따라 단위 테스트가 진행 될 예정이므로, 구현 **마지막 단계**에 main.py가 포함될 수 있도록 해야합니다.
4. 작성한 내용을 협업자 모두 follow 할 수 있도록 **아래 format을 엄격히 준수**해야 합니다.

**format**:
<sequence>
1. PATH/FILENAME: Key function and role
2. PATH/FILENAME: Key function and role
3. ...
...
<sequence/>


스켈레톤코드:
{skeleton_code}
프로젝트 구조:
{initial_structure}

"""
assistant_role_name: str = "Software_Architect"
assistant_role_prompt: str = """이번 고객의 요청한 요구 사항은 \"{task}\"입니다.
당신은 뛰어난 소프트웨어 아키텍트로서, 복잡한 시스템의 구조와 구성 요소 간의 의존성을 명확하게 이해하고 관리할 수 있습니다.
프로젝트의 전체적인 아키텍처를 설계하고, 각 기능의 구현 우선순위를 결정하여 효율적인 개발 프로세스를 이끌어냅니다.]
"""