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


## 추가된 메서드


import os
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

# 메서드 추가

def install_missing_modules(error_message, container):
    import re
    import docker

    # 오류 메시지에서 누락된 모듈 이름 추출
    match = re.search(r"No module named '([^']+)'", error_message)
    if match:
        module_name = match.group(1)
        print(f"Installing missing module: {module_name}")

        # 모듈 이름 검증
        if not re.match(r'^[a-zA-Z0-9_\-]+$', module_name):
            print(f"Invalid module name detected: {module_name}")
            return "Could not extract module name from error message.", False

        # 모듈 설치
        try:
            # Docker SDK를 사용하여 컨테이너 내에서 pip install 실행
            install_command = f"python -m pip install {module_name}"
            exec_install = container.exec_run(install_command)
            install_output = exec_install.output.decode('utf-8', errors='ignore')
            install_exit_code = exec_install.exit_code

            if install_exit_code == 0:
                print(f"Successfully installed module: {module_name}")
                return install_output, True
            else:
                print(f"Failed to install module {module_name}. Output:\n{install_output}")
                return install_output, False

        except Exception as e:
            print(f"Exception occurred while installing module {module_name}: {e}")
            return e, False
    else:
        print("Could not extract module name from error message.")
        return "Could not extract module name from error message.", False

import os
import re
import time
import threading
import docker

def verify_functionality(file_path, file_name, container, directory, retries=0, max_retries=3, base_path="project"):
    import time
    datetime_string = time.strftime("%y%m%d%H%M%S")
    if retries > max_retries:
        print("Maximum retry limit reached.")
        return "Maximum retry limit reached.", False
    
    # 기존 경로 설정 로직
    potential_path = os.path.join(directory, base_path, file_path, file_name)
    norm_path = os.path.normpath(potential_path) if os.path.exists(potential_path) else next(
        (os.path.normpath(os.path.join(root, file_name)) for root, _, files in os.walk(os.path.join(directory, base_path)) if file_name in files), "")

    modelservedfile = os.path.splitext(re.sub(r"[\\/]", ".", os.path.join(file_path, file_name)))[0]

    project_root = os.path.join(directory, base_path)
    rel_path = os.path.relpath(norm_path, project_root)
    
    project_name = rel_path.split(os.sep)[0]
    cd_path = os.path.join(project_root, project_name)
    print(f"""cd_path: {cd_path}
modelservedfile: {modelservedfile}
project_root: {project_root}
rel_path: {rel_path}
""")

    timeout_duration = 10 # TODO: 추후 상위에서 설정할 수 있으면 좋을듯    
    command = f"timeout {timeout_duration}s bash -c 'cd .. && cd \"{cd_path}\" && xvfb-run -a -s \"-screen 0 1024x768x24\" python -m {modelservedfile}'"


    # Docker SDK를 사용하여 컨테이너에 연결
    client = docker.from_env()

    # 컨테이너 객체 확인
    if isinstance(container, str):
        container = client.containers.get(container)

    try:
        # 명령을 비동기적으로 실행하고 출력 스트림을 캡처
        exec_instance = client.api.exec_create(container.id, command, tty=False)
        exec_id = exec_instance['Id']
        output_generator = client.api.exec_start(exec_id, detach=False, tty=False, stream=True)
        print(f"Command started with exec_id: {exec_id}")

        # 타임아웃 설정
        timeout = 10  # 원하는 타임아웃 시간(초)
        start_time = time.time()

        output_lines = []

        def read_output():
            nonlocal output_generator, output_lines
            try:
                for chunk in output_generator:
                    decoded_chunk = chunk.decode('utf-8', errors='ignore')
                    output_lines.append(decoded_chunk)
                    print(decoded_chunk, end='')
            except Exception as e:
                print(f"Output reading error: {e}")

        # 출력 읽기 스레드 시작
        output_thread = threading.Thread(target=read_output)
        output_thread.start()

        # 실행 상태를 모니터링하는 함수
        def monitor_exec():
            nonlocal exec_id, container
            while True:
                exec_info = client.api.exec_inspect(exec_id)
                if not exec_info['Running']:
                    print("Command completed.")
                    break
                if time.time() - start_time > timeout:
                    print("Timeout reached. Sending SIGINT to the process.")
                    # 프로세스에 SIGINT 신호 보내기
                    pid = exec_info.get('Pid')
                    if pid:
                        container.exec_run(f"kill -2 {pid}", detach=True, privileged=True)
                    else:
                        print("Unable to get PID of the process.")
                    break
                time.sleep(1)

        # 모니터링 스레드 시작
        monitor_thread = threading.Thread(target=monitor_exec)
        monitor_thread.start()

        # 스레드들이 종료되길 기다림
        output_thread.join(timeout + 5)
        monitor_thread.join(timeout + 5)

        # 실행 결과 확인
        exec_info = client.api.exec_inspect(exec_id)
        exit_code = exec_info['ExitCode']
        is_step_complete = (exit_code == 0)

        # 출력 내용을 결합
        output = ''.join(output_lines)
        
        if exit_code == 124:
            error_code = f"Timeout occurred after {timeout_duration} seconds."
            return error_code+datetime_string, False

        
        if not is_step_complete:
            error_code = f"Exit code: {exit_code}\nOutput:\n{output}"

            # ModuleNotFoundError 처리
            if 'ModuleNotFoundError' in output and retries < max_retries:
                install_output, success = install_missing_modules(output, container)
                if success:
                    # 모듈 설치 후 재시도
                    return verify_functionality(file_path, file_name, container, directory, retries=retries, max_retries=max_retries)
                else:
                    print("Module installation failed or import error.")
                    return install_output, False
            else:
                # 기타 오류 처리
                return error_code+datetime_string, False
        else:
            error_code = f"Exit code: {exit_code}\nOutput:\n{output}"

    except Exception as e:
        is_step_complete = False
        error_code = str(e)
        # 예외 발생 시 처리
        return error_code+datetime_string, is_step_complete

    return error_code+datetime_string, is_step_complete


def extract_test_file(seminar_conclusion: str) -> tuple:
    test_file_pattern = re.compile(r"<Test this>([^<]+)<Test this/>")
    lines = seminar_conclusion.strip().splitlines()
    for line in reversed(lines):
        match = test_file_pattern.search(line)
        if match:
            full_path = match.group(1).strip()
            path_parts = full_path.rsplit('/', 1)
            if len(path_parts) == 2:
                return tuple(path_parts)  # (PATH, FILENAME)
            else:
                return (path_parts[0], '')  # FILENAME이 없는 경우 PATH만 반환
    
    # 형식이 맞지 않을 경우 None 반환
    return None

def count_steps(impl_step: str) -> int:
    numbers = re.findall(r'^\s*(\d+)\.', impl_step, re.MULTILINE)
    return len(numbers)


import shutil
def remove_pycache_dirs(directory):
    base_path:str = directory
    if not os.path.isdir(base_path):
        print(f"디렉토리가 존재하지 않습니다: {base_path}")
        return

    for root, dirs, files in os.walk(base_path, topdown=False):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"삭제됨: {dir_path}")
                except Exception as e:
                    print(f"삭제 실패: {dir_path}. 오류: {e}")

from typing import Tuple, List
import time
def validate_response_format(response_text: str) -> Tuple[str, bool]:
    datetime_string = time.strftime("%y%m%d%H%M%S")
    lines = response_text.strip().split('\n')
    if lines and lines[0].strip() and not lines[0].strip().startswith('#'): 
        return (f"이전 응답에서 반환 형식을 위반하여 코드 실행 전에 재응답을 요청하였습니다.:\n위반사유:첫 줄부터 # 헤더로 작성하세요. ``` ``` 로 감싸는것은 코드블록에만 사용해야 합니다.{datetime_string}", False)
    header_pattern = re.compile(r'^(#+)\s+(.+)/\s*$')
    file_pattern = re.compile(r'^(#+)\s+([\w/]+\.py)\s*$')
    test_tag_pattern = re.compile(r'<Test this>([\w/]+\.py)<Test this/>')
    
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
        return (f"이전 응답에서 반환 형식을 위반하여 코드 실행 전에 재응답을 요청하였습니다.:\n위반사유:#으로 프로젝트 트리구조를 구분하여 작성되지 않았습니다.{datetime_string}", False)
    
    min_hash = min(header[0] for header in headers)
    top_level_dirs = [header for header in headers if header[0] == min_hash]
    
    if len(top_level_dirs) != 1:
        return (f"이전 응답에서 반환 형식을 위반하여 코드 실행 전에 재응답을 요청하였습니다.:\n위반사유:최상단 디렉토리 부터 트리 구조가 구분 되도록 #으로 작성해야 합니다.{datetime_string}", False)
    
    top_level_dir_name = top_level_dirs[0][1]
    
    # 헤더 정보를 이용하여 디렉토리 구조 생성
    current_path = []
    dir_stack = []
    header_index = 0  # 헤더 인덱스 초기화
    
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
            file_dir = dir_stack[:expected_depth]
            file_path = '/'.join(file_dir) + '/' + file_name
            project_files.append(file_path)
    
    # 최상위 디렉토리를 제거하여 상대 경로로 변환
    project_files = [fp[len(top_level_dir_name)+1:] if fp.startswith(top_level_dir_name + '/') else fp for fp in project_files]
    print(f"project_files: {project_files}")
    # 테스트 파일 추출
    test_files = test_tag_pattern.findall(response_text)
    print(f"test_files: {test_files}")
    if not test_files:
        return (f"이전 응답에서 반환 형식을 위반하여 코드 실행 전에 재응답을 요청하였습니다.:\n위반사유:'<Test this>PATH/FILENAME<Test this/>' 형식의 태그가 작성되지 않았습니다.{datetime_string}", False)
    
    # 테스트 파일이 프로젝트 내에 존재하는지 확인
    missing_files = [file for file in test_files if file not in project_files]
    
    if missing_files:
        missing_str = ', '.join(missing_files)
        return (f"이전 응답에서 반환 형식을 위반하여 코드 실행 전에 재응답을 요청하였습니다.:\n위반사유:테스트 파일은 프로젝트 구조 내에 존재 해야 합니다.\
이전에 작성 되어 있던 내용과 구조가 당신이 제출한 프로젝트 구조와 일치하지 않을 수 있습니다.{datetime_string}", False)
    
    return ("형식이 올바릅니다.", True)

import docker

def build_docker_image(path: str, tag: str) -> bool:
    """
    지정된 경로의 Dockerfile을 기반으로 Docker 이미지를 빌드합니다.
    
    Parameters:
        path (str): Dockerfile이 위치한 디렉토리 경로.
        tag (str): 빌드된 이미지에 할당할 태그.
    
    Returns:
        bool: 빌드 성공 여부 (성공하면 True, 실패하면 False).
    """
    client = docker.from_env()
    try:
        client.images.build(path=path, tag=tag, rm=True)
        print(f"Docker 이미지 '{tag}'가 성공적으로 빌드되었습니다.")
        return True
    except docker.errors.BuildError as e:
        print(f"이미지 빌드 실패: {e}")
        return False
    except docker.errors.APIError as e:
        print(f"Docker API 오류: {e}")
        return False
