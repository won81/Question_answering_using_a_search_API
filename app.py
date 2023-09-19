import re
import json
import requests
import streamlit as st
from bardapi.constants import SESSION_HEADERS
from bardapi import Bard
from streamlit_chat import message

st.header('Bard 를 이용한 QA (구현 중)')

if 'generated_responses' not in st.session_state:
    st.session_state['generated_responses'] = []

if 'user_inputs' not in st.session_state:
    st.session_state['user_inputs'] = []

if 'psid' not in st.session_state:
    st.session_state['psid'] = ''

if 'psidts' not in st.session_state:
    st.session_state['psidts'] = ''

if 'psidcc' not in st.session_state:
    st.session_state['psidcc'] = ''

st.session_state['psid'] = st.text_input('1PSID: ', st.session_state['psid'])
st.session_state['psidts'] = st.text_input('1PSIDTS: ', st.session_state['psidts'])
st.session_state['psidcc'] = st.text_input('1PSIDCC: ', st.session_state['psidcc'])

session = requests.Session()
session.headers = SESSION_HEADERS
session.cookies.set("__Secure-1PSID", st.session_state.psid)
session.cookies.set("__Secure-1PSIDTS", st.session_state.psidts)
session.cookies.set("__Secure-1PSIDCC", st.session_state.psidcc)


def get_question_queries(payload):
    # bard = Bard(token=st.session_state.psid, session=session)
    bard = Bard(token_from_browser=True)
    prompt = '\
            {"role": "system", "content": "Output only valid JSON"},\
            {"role": "user", "content": "\
            You have access to a search API that returns recent news articles. \
            Generate an array of search queries that are relevant to this question. \
            Use a variation of related keywords for the queries, trying to be as general as possible. \
            Include as many queries as you can think of, including and excluding terms. \
            For example, include queries like [\'keyword_1 keyword_2\', \'keyword_1\', \'keyword_2\']. \
            Be creative. The more queries you include, the more likely you are to find relevant results.\
            User question: ' + payload + '\
            Format: {{"queries": ["query_1", "query_2", "query_3"]}}}'

    response = bard.get_answer(prompt)
    return response

def get_json(json_string):
    json_string = json_string.replace('\n', ' ')
    result = re.search('```json(.*)```', json_string)
    return json.loads(result.group(1))

with st.form('form', clear_on_submit = True):
    user_input = st.text_input('Message: ', '')
    submitted = st.form_submit_button('Send')

if submitted and user_input:
    output = get_question_queries(user_input)
    json_object = get_json(output['content'])
    print(json_object['queries'])

    st.session_state.user_inputs.append(user_input)
    st.session_state.generated_responses.append(str(json_object['queries']))

if st.session_state['generated_responses']:
    index = len(st.session_state['generated_responses']) - 1
    message(st.session_state['user_inputs'][index], is_user = True, key=str(index) + '_user')
    message(st.session_state['generated_responses'][index], key=str(index))


