import os
import re
from typing import List, Dict

import re
from typing import List, Dict

def parse_text(input_str: str) -> List[Dict[str, str]]:
    """
    Parses the input string representing the project structure and extracts
    the file paths and code blocks.

    Args:
        input_str (str): The project structure string to parse.

    Returns:
        List[Dict[str, str]]: A list of dictionaries with 'path', 'code', and 'type' keys.
    """
    path_stack = []  # Stack to keep track of current path
    result = []      # List to store the final result
    in_code_block = False
    code_block_lang = ''
    code_lines = []
    current_file = None

    # Regular expressions to match headers and code blocks
    header_pattern = re.compile(r'^(#{1,6})\s+(.*)')
    code_block_start_pattern = re.compile(r'^```(\w+)?')
    code_block_end_pattern = re.compile(r'^```$')

    lines = input_str.splitlines()

    # Find the minimum header level to determine the base level
    header_levels = []
    for line in lines:
        header_match = header_pattern.match(line)
        if header_match:
            hashes, _ = header_match.groups()
            level = len(hashes)
            header_levels.append(level)

    if not header_levels:
        base_level = 1  # Default base level if no headers are found
    else:
        base_level = min(header_levels)

    for line in lines:
        line = line.rstrip()
        # Code block start
        if not in_code_block and code_block_start_pattern.match(line):
            in_code_block = True
            code_block_lang = code_block_start_pattern.match(line).group(1) or ''
            code_lines = []
            continue

        # Code block end
        if in_code_block and code_block_end_pattern.match(line):
            in_code_block = False
            code = '\n'.join(code_lines).strip()
            if current_file:
                full_path = '/'.join(path_stack + [current_file])
                result.append({
                    'path': full_path,
                    'code': code,
                    'type': 'file'
                })
                current_file = None
            else:
                # If there's code but no current file, associate it with the current directory
                full_path = '/'.join(path_stack)
                result.append({
                    'path': full_path,
                    'code': code,
                    'type': 'directory'
                })
            continue

        # Inside code block
        if in_code_block:
            code_lines.append(line)
            continue

        # Header line
        header_match = header_pattern.match(line)
        if header_match:
            hashes, heading_text = header_match.groups()
            level = len(hashes)
            depth = level - base_level

            # Adjust the path stack to match the current depth
            if depth < 0:
                path_stack = []
            else:
                while len(path_stack) > depth:
                    path_stack.pop()

            # Split the heading text from any description after a colon
            heading_parts = heading_text.split(':', 1)
            heading_name = heading_parts[0].strip()

            if heading_name.endswith('/'):
                # It's a directory
                directory = heading_name.rstrip('/')
                path_stack.append(directory)
                result.append({
                    'path': '/'.join(path_stack),
                    'code': '',
                    'type': 'directory'
                })
                current_file = None
            else:
                # It's a file
                current_file = heading_name
            continue

    return result

def validate_response_format(response_text: str):
    import re

    lines = response_text.strip().split('\n')
    if lines and lines[0].strip().startswith('```'):
        return ("이전 작성 시도에 대한 응답: ``` ``` 블록은 파일 코드와 docstring을 적은 내용에 사용해야 합니다.", False)
    
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)/\s*$')
    file_pattern = re.compile(r'^(#{1,6})\s+([\w/]+\.py)\s*$')
    
    headers = []
    project_files = []
    current_path = []
    
    for line in lines:
        header_match = header_pattern.match(line)
        file_match = file_pattern.match(line)
        
        if header_match:
            num_hashes = len(header_match.group(1))
            dir_name = header_match.group(2).rstrip('/')
            headers.append((num_hashes, dir_name))
    
    if not headers:
        return ("이전 작성 시도에 대한 응답: #으로 레벨을 구분하여 표현된 프로젝트 디렉토리가 없습니다.", False)
    
    min_hash = min(header[0] for header in headers)
    top_level_dirs = [header for header in headers if header[0] == min_hash]
    
    if len(top_level_dirs) != 1:
        return ("이전 작성 시도에 대한 응답: 코드 작성은 최상단 디렉토리 부터 #으로 트리구조가 구분되도록 작성 해야 합니다.", False)
    
    top_level_dir_name = top_level_dirs[0][1]
    
    # 헤더 정보를 이용하여 디렉토리 구조 생성
    current_path = []
    dir_stack = []
    
    for line in lines:
        header_match = header_pattern.match(line)
        file_match = file_pattern.match(line)
        
        if header_match:
            num_hashes = len(header_match.group(1))
            dir_name = header_match.group(2).rstrip('/')
            expected_depth = num_hashes - min_hash
            while len(dir_stack) > expected_depth:
                dir_stack.pop()
            dir_stack.append(dir_name)
            current_path = dir_stack.copy()
        elif file_match:
            num_hashes = len(file_match.group(1))
            file_name = file_match.group(2)
            expected_depth = num_hashes - min_hash
            while len(dir_stack) > expected_depth:
                dir_stack.pop()
            file_dir = dir_stack[:]
            file_path = '/'.join(file_dir) + '/' + file_name
            project_files.append(file_path)
    
    # 최상위 디렉토리를 제거하여 상대 경로로 변환
    project_files = [fp[len(top_level_dir_name)+1:] if fp.startswith(top_level_dir_name + '/') else fp for fp in project_files]
    print(f"project_files: {project_files}")
    
    # 'test' 또는 'tests' 디렉토리 내의 '__init__.py' 파일 존재 여부 확인
    test_init_exists = False
    for test_dir_name in ['test', 'tests']:
        test_init = f'{test_dir_name}/__init__.py'
        if test_init in project_files:
            test_init_exists = True
            break
    
    if not test_init_exists:
        return ("'test/__init__.py' 또는 'tests/__init__.py' 파일이 스켈레톤 코드에 작성되어 있어야 합니다. 또한 빈 디렉토리는 __init__.py를 작성 해야 합니다.", False)
    
    return ("형식이 올바릅니다.", True)

import difflib
def rewrite_codes(files, base_path='.', diff_output_dir=None, proj_dir="project"):
    project_path = os.path.join(base_path, proj_dir)

    # Ensure the 'project' folder exists
    if not os.path.isdir(project_path):
        try:
            os.makedirs(project_path, exist_ok=True)
            print(f"{proj_dir} folder created at: {project_path}")
        except (IOError, OSError) as e:
            print(f"Cannot create {proj_dir} folder. Error: {e}")
            return

    base_path = project_path
    print(f"files:\n\n{files}\n\n")
    for file in files:
        normalized_path = os.path.normpath(file['path'])
        file_path = os.path.join(base_path, normalized_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        print(f"Processing: {normalized_path}")
        print(f"file_path: {file_path}")

        if file['type'] == 'directory':
            # Create the directory if it doesn't exist
            os.makedirs(file_path, exist_ok=True)
            print(f"Created directory {file_path}")
            continue

        new_code_lines = file['code'].splitlines(keepends=True)

        if os.path.exists(file_path):
            # Read the existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_code_lines = f.readlines()

            # Create a diff
            diff = difflib.unified_diff(
                existing_code_lines, new_code_lines,
                fromfile=f'original/{file["path"]}',
                tofile=f'updated/{file["path"]}',
                lineterm=''
            )
            diff_text = '\n'.join(diff)

            if diff_text:
                # Update the file if there are changes
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_code_lines)
                print(f"Updated code in {file_path}")

                # Output the diff
                print(f"Changes in {file_path}:\n{diff_text}\n")

                # Optionally save the diff to a file
                if diff_output_dir:
                    diff_file_path = os.path.join(diff_output_dir, f'{file["path"]}.diff')
                    diff_dir = os.path.dirname(diff_file_path)
                    os.makedirs(diff_dir, exist_ok=True)
                    with open(diff_file_path, 'w', encoding='utf-8') as diff_file:
                        diff_file.write(diff_text)
                    print(f"Saved diff to {diff_file_path}")
            else:
                print(f"No changes detected in {file_path}")
        else:
            # Create a new file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_code_lines)
            print(f"Created new file {file_path}")