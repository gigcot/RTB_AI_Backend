import os

def load_codes_from_hardware(base_path):
    structure_lines = []
    project_path = os.path.join(base_path, 'project')

    # 'project' 폴더가 존재하는지 확인
    if not os.path.isdir(project_path):
        print(f"'project' 폴더가 {base_path} 내에 존재하지 않습니다.")
        return ""
    
    # 'project' 폴더 내부의 하위 폴더 리스트 가져오기
    subdirs = [d for d in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, d))]
    
    if not subdirs:
        print(f"'project' 폴더 내에 하위 폴더가 존재하지 않습니다.")
        return ""
    
    # 'project' 폴더 내부의 모든 하위 폴더를 순회
    for subdir in subdirs:
        subdir_path = os.path.join(project_path, subdir)
        for root, dirs, files in os.walk(subdir_path):
            rel_path = os.path.relpath(root, project_path)
            if rel_path == subdir:
                level = 3  # 최상위 하위 폴더는 ###로 시작
                heading = '### ' + os.path.basename(root) + '/'
            else:
                depth = rel_path.count(os.sep)
                level = min(depth + 3, 6)  # 최대 헤딩 레벨을 6으로 제한
                heading = '#' * level + ' ' + os.path.basename(root) + '/'

            structure_lines.append(heading)

            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                    except Exception as e:
                        code_content = f"파일을 읽는 중 오류 발생: {e}"

                    file_heading = '#' * (level + 1) + ' ' + filename
                    structure_lines.append('')
                    structure_lines.append(file_heading)
                    structure_lines.append('```python')
                    structure_lines.append(code_content)
                    structure_lines.append('```')
                    structure_lines.append('')
                else:
                    # .py 파일이 아닌 경우 처리하지 않음 (필요에 따라 수정 가능)
                    pass
    result = '\n'.join(structure_lines)
    return result