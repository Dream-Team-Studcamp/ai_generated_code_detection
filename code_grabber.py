import os
import re
import shutil

from pathlib import Path

RE_FUNCTION_PATTERN = re.compile(
    r'([a-zA-Z_][a-zA-Z0-9_*\s]*\s+\**\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})'
)


def extract_c_functions(code: str) -> list[str]:
    return RE_FUNCTION_PATTERN.findall(code)


def extract_c_functions_from_repository(
    repo_url: str,
    validate_functions: bool = False,
    return_file: bool = False,
) -> list[str] | list[tuple[str, str]]:
    dir_name = repo_url.split('/')[-1].rstrip('.git')
    dir_name = f'___{dir_name}___'
    root = Path(dir_name)

    try:
        print(f'Cloning {repo_url}')
        os.system(f'git clone {repo_url} {dir_name}')
        functions = []
        for path_object in root.rglob('*.c'):
            if path_object.is_file():
                code = path_object.read_text()

                file_functions = extract_c_functions(code)
                if validate_functions:
                    file_functions = filter(validate, file_functions)

                if return_file:
                    file_functions = [
                        (function, str(path_object).split(dir_name)[1].lstrip('/'))
                        for function in file_functions
                    ]

                functions.extend(file_functions)
        print(f'Extracted {len(functions)} functions')
        return functions
    finally:
        shutil.rmtree(root)


def validate(function):
    start = 'else', 'end', 'if', 'ifdef', 'ifndef', 'endif', 'define'
    return all(not function.startswith(s) for s in start)


if __name__ == '__main__':
    repositories = [
        'https://github.com/TheAlgorithms/C.git',
        'https://github.com/Genymobile/scrcpy.git',
        'https://github.com/curl/curl.git',
        'https://github.com/itookyourboo/graph-database.git',
    ]

    functions = sum(map(extract_c_functions_from_repository, repositories), [])
    functions = list(filter(validate, functions))
