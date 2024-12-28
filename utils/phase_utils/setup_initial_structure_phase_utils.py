from typing import Tuple

def check_answer_in_init_structure(answer_str: str) -> Tuple[str, bool, str]:
    import re

    error_messages = []
    pass_check = True
    code_block_content = ""

    # 코드 블록 추출을 위한 정규표현식 패턴
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, answer_str, re.DOTALL)

    if not matches:
        error_messages.append("답변은 ```로 시작하고 ```로 끝나야 하며, 그 안에 내용이 있어야 합니다.")
        pass_check = False
    else:
        code_block_content = matches[0].strip()
        if not code_block_content:
            error_messages.append("코드 블록 안에 내용이 없습니다.")
            pass_check = False
        else:
            lines = code_block_content.strip().splitlines()
            if len(lines) < 2:
                error_messages.append("코드 블록 안에 디렉토리 구조가 없습니다.")
                pass_check = False
            else:
                # 번호 체계를 기반으로 계층 구조 파싱
                hierarchy = {}
                parent_stack = []
                top_level_nodes = []
                for line in lines:
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue  # 빈 라인 건너뜀

                    # 번호와 내용 분리
                    match = re.match(r'(\d+(\.\d+)*)\s+(.*)', stripped_line)
                    if match:
                        num_str, _, content = match.groups()
                        num_parts = num_str.split('.')
                        level = len(num_parts)

                        # 파일명과 설명 분리
                        content_parts = content.split(':', 1)
                        content_name = content_parts[0].strip()
                        description = content_parts[1].strip() if len(content_parts) > 1 else ''

                        # 파일과 디렉토리 구분
                        if content_name.endswith('/'):
                            node_type = 'directory'
                            content_name = content_name.rstrip('/')
                        else:
                            node_type = 'file'

                        node = {
                            'number': num_str,
                            'content': content_name,
                            'type': node_type,
                            'children': []
                        }

                        # 현재 레벨에 맞게 부모 스택 조정
                        while len(parent_stack) >= level:
                            parent_stack.pop()

                        if parent_stack:
                            parent_stack[-1]['children'].append(node)
                        else:
                            hierarchy[num_str] = node
                            top_level_nodes.append(node)  # 최상위 노드로 추가

                        parent_stack.append(node)
                    else:
                        # 번호 체계가 없는 경우 무시하거나 오류 처리 가능
                        continue

                # 최상위 레벨 항목 수 검사
                if len(top_level_nodes) != 1:
                    error_messages.append("최상위 디렉토리와 같은 레벨에 다른 디렉토리나 파일이 있어서는 안 됩니다.")
                    pass_check = False

                # test 디렉토리 검사 함수 정의
                def check_test_dirs(node):
                    nonlocal pass_check
                    # 'test'로 시작하고 정확히 일치하는 디렉토리 찾기
                    if node['type'] == 'directory' and re.match(r'^test[s]?$', node['content']):
                        if not node['children']:
                            error_messages.append(f"'{node['content']}/' 디렉토리에는 '__init__.py' 파일이 포함되어 있어야 합니다.")
                            pass_check = False
                        elif len(node['children']) > 1:
                            error_messages.append(f"'{node['content']}/' 디렉토리에는 '__init__.py' 파일만 포함되어 있어야 합니다.")
                            pass_check = False
                        else:
                            child = node['children'][0]
                            if child['type'] != 'file' or child['content'] != '__init__.py':
                                error_messages.append(f"'{node['content']}/' 디렉토리에는 '__init__.py' 파일만 포함되어 있어야 합니다.")
                                pass_check = False
                    # 자식 노드에 대해 재귀적으로 검사
                    for child in node['children']:
                        check_test_dirs(child)

                # 최상위 노드에 대해 test 디렉토리 검사 실행
                for node in top_level_nodes:
                    check_test_dirs(node)

    error_message = '\n'.join(error_messages) if error_messages else "OK"
    return error_message, pass_check, code_block_content

