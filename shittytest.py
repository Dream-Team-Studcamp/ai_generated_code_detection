import sys
import json
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import code_grabber

print('Loading model...')
with open('pickled_model.pkl', 'rb') as file:
    classifier: LogisticRegression = pickle.load(file)

print('Loading embedder...')
embedder = SentenceTransformer('microsoft/graphcodebert-base', trust_remote_code=True)


def check_code(code: str) -> tuple[float, float]:
    embedded_code = embedder.encode(code)
    return classifier.predict_proba([embedded_code])[0]

repositories = [                                          #     AI / All
    'https://github.com/TheAlgorithms/C.git',             # ==== 81/1226 ====
    'https://github.com/Genymobile/scrcpy.git',           # ==== 34/657  ====
    'https://github.com/curl/curl.git',                   # ====  5/3516 ====
    'https://github.com/itookyourboo/graph-database.git', # ==== 26/564  ====
    'https://github.com/Huawei/Huawei_LiteOS_Kernel.git'  # ==== 16/119  ====
]

for repo in repositories:
    print(f'Extracting functions from {repo}')
    functions = code_grabber.extract_c_functions_from_repository(repo)
    functions = list(filter(code_grabber.validate, functions))
    print(f'Extracted {len(functions)} functions')
    k = 0
    for i, code in enumerate(functions):
        robot, human = check_code(code)
        human_rounded = round(100 * human, 2)
        robot_rounded = round(100 - human_rounded, 2)
        written_by = 'Human' if human_rounded > robot_rounded else 'AI'
        if written_by == 'Human':
            k += 1
        print(f'{repo}:{i} was written by {written_by} ({max(human_rounded, robot_rounded)}%)')
    print(f'==== {k}/{len(functions)} ====')

# ==== 81/1226 ====
