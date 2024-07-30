import pickle
import streamlit as st

from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

with open('pickled_model.pkl', 'rb') as file:
    classifier: LogisticRegression = pickle.load(file)

embedder = SentenceTransformer('microsoft/graphcodebert-base', trust_remote_code=True)


def check_code(code: str) -> tuple[float, float]:
    embedded_code = embedder.encode(code)
    return classifier.predict_proba([embedded_code])[0]


st.title('AI Generated C/C++ Code Detection')
st.text('F1 score on 800 production codes was 0.95')
user_input = st.text_area('Enter code:', max_chars=2048)

if st.button('Check'):
    robot, human = check_code(user_input)
    human_rounded = round(100 * human, 2)
    robot_rounded = round(100 - human_rounded, 2)
    written_by = 'Human' if human_rounded > robot_rounded else 'AI'
    st.write(f'This code was written by **{written_by}** ({max(human_rounded, robot_rounded)}%)')