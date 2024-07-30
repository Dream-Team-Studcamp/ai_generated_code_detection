import pickle
import streamlit as st

from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

from code_grabber import extract_c_functions_from_repository


@st.cache_resource
def load_model() -> LogisticRegression:
    with open('pickled_model.pkl', 'rb') as file:
        return pickle.load(file)


@st.cache_resource
def load_embedder() -> SentenceTransformer:
    return SentenceTransformer('microsoft/graphcodebert-base', trust_remote_code=True)


classifier = load_model()
embedder = load_embedder()


def check_code(code: str) -> tuple[float, float]:
    embedded_code = embedder.encode(code)
    return classifier.predict_proba([embedded_code])[0]


st.title('AI Generated C/C++ Code Detection')
st.text('F1 score on 800 production codes was 0.95')

tab1, tab2 = st.tabs(['Check code', 'Scan repository'])

with tab1:
    st.header('Check code')
    user_input = st.text_area('Enter code:', max_chars=2048, height=400)

    if st.button('Check'):
        robot, human = check_code(user_input)
        human_rounded = round(100 * human, 2)
        robot_rounded = round(100 - human_rounded, 2)
        written_by = 'Human' if human_rounded > robot_rounded else 'AI'
        st.write(f'This code was written by **{written_by}** ({max(human_rounded, robot_rounded)}%)')

with tab2:
    st.header('Scan repository')
    repository_url = st.text_input('GitHub repository URL:')

    if st.button('Scan'):
        with st.spinner('Extracting functions from repository'):
            references = extract_c_functions_from_repository(
                repo_url=repository_url,
                validate_functions=True,
                return_file=True,
            )

        n = len(references)
        analyze_bar = st.progress(0, text='Analyze functions')

        ai_generated = []
        for i, (code, file) in enumerate(references, 1):
            robot, _ = check_code(code)
            analyze_bar.progress(i / n)
            if robot > .5:
                ai_generated.append((code, file, robot))

        st.subheader(f'AI Generated Code From Repository ({len(ai_generated)} / {n})')
        for code, file, prob in sorted(ai_generated, key=lambda x: -x[-1]):
            link = f'{repository_url.rstrip(".git")}/blob/master/{file}'
            st.write(f'{prob:.2%}: [{file}]({link})')
            st.code(code, language='cpp')
