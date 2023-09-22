import re
import json
import requests
import streamlit as st
from bardapi.constants import SESSION_HEADERS
from bardapi import Bard
from streamlit_chat import message

st.header('Bard와 Newsapi를 이용한 뉴스 검색 서비스')
st.markdown("[Detailed explanation](https://wide-shallow.tistory.com/)")

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

if 'news_api_key' not in st.session_state:
    st.session_state['news_api_key'] = ''

st.session_state['psid'] = st.text_input('1PSID: ', st.session_state['psid'])
st.session_state['psidts'] = st.text_input('1PSIDTS: ', st.session_state['psidts'])
st.session_state['psidcc'] = st.text_input('1PSIDCC: ', st.session_state['psidcc'])
st.session_state['news_api_key'] = st.text_input('NEWS API KEY: ', st.session_state['news_api_key'])

session = requests.Session()
session.headers = SESSION_HEADERS
session.cookies.set("__Secure-1PSID", st.session_state.psid)
session.cookies.set("__Secure-1PSIDTS", st.session_state.psidts)
session.cookies.set("__Secure-1PSIDCC", st.session_state.psidcc)

import browser_cookie3

def get_question_queries(payload):
    bard = Bard(token=st.session_state.psid, session=session)
    prompt = '\
            {"role": "system", "content": "Output only valid JSON"},\
            {"role": "user", "content": "\
            You have access to a search API that returns recent news articles. \
            If you know the date involved in the question, please change it to yyyy-mm-dd format. \
            Generate an array of search queries that are relevant to this question. \
            Use a variation of related keywords for the queries, trying to be as general as possible. \
            Include as many queries as you can think of, including and excluding terms. \
            When creating queries, remove words that refer to datetime like yesterday, today, days, and month. \
            Make the query an English word. \
            For example, include queries like [\'keyword_1 keyword_2\', \'keyword_1\', \'keyword_2\']. \
            Be creative. The more queries you include, the more likely you are to find relevant results.\
            User question: ' + payload + '\
            Format: {{"queries": ["query_1", "query_2", "query_3"], "date": {"from": "yyyy-mm-dd", "to": "yyyy-mm-dd"}}}'

    response = bard.get_answer(prompt)
    return response

def get_json(json_string):
    json_string = json_string.replace('\n', ' ')
    result = re.search('```json(.*)```', json_string)
    return json.loads(result.group(1))

with st.form('form', clear_on_submit = True):
    user_input = st.text_input('Message: ', '')
    submitted = st.form_submit_button('Send')

def search_news(
        query: str,
        news_api_key: str = st.session_state.news_api_key,
        num_articles: int = 10,
        from_datetime: str = "2023-09-01", 
        to_datetime: str = "2023-09-15",
) -> dict:
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": query,
            "apiKey": news_api_key,
            "pageSize": num_articles,
            "sortBy": "relevancy",
            "from": from_datetime,
            "to": to_datetime,
        },
    )
    return response.json()

if submitted and user_input:
    output = get_question_queries(user_input)
    json_object = get_json(output['content'])
    queries = json_object['queries']
    dates = json_object['date']

    articles = []

    # for query in queries:
    result = search_news(queries[0], from_datetime = dates["from"], to_datetime = dates["to"])
    if result["status"] == "ok":
        articles = articles + result["articles"]
    else:
        raise Exception(result["message"])

    articles = list({article["url"]: article for article in articles}.values())

    generated_text = ""
    for article in articles[0:5]:
        generated_text += "Title: " + article["title"] + "\n"
        generated_text += "Description: " + article["description"] + "\n"
        generated_text += "Content: " + article["content"][0:100] + "\n\n\n"

    st.session_state.user_inputs.append(user_input)
    st.session_state.generated_responses.append(generated_text)

if st.session_state['generated_responses']:
    index = len(st.session_state['generated_responses']) - 1
    message(st.session_state['user_inputs'][index], is_user = True, key=str(index) + '_user')
    message(st.session_state['generated_responses'][index], key=str(index))

