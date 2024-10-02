import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import json
import time
import urllib.parse
import urllib.request
from openai import OpenAI
import os

st.title('Trivia Questions For Right Now')

@st.cache_data
def wiki_trending_today(n):
    """Grab n trending wikipedia articles from today
    Returns a tuple, (titles, extracts)"""
    today = datetime.datetime.now()
    date = today.strftime('%Y/%m/%d')
    language_code = 'en'

    headers = {
        'Authorization': st.secrets["wiki_key"],
        'User-Agent': st.secrets["User-Agent"]
    }
    base_url = 'https://api.wikimedia.org/feed/v1/wikipedia/'
    url = base_url + language_code + '/featured/' + date
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    titles= []
    extracts=[]
    for i in response['mostread']['articles'][:n]:
        if 'description' in i.keys():
            titles.append(i['titles']['normalized'])
            extracts.append(i['extract'])
    return titles, extracts

@st.cache_data
def find_corresponding_news(titles, n, m):
    """given a list of titles, collect news articles corresponding to the first n titles
    Returns a list of strings, where each string can be used as a context for LLM
    """
    gnews_key=st.secrets["gnews_key"]
    all_contexts=[]
    for title in titles[:n]:
        context=[]
        url = f'https://gnews.io/api/v4/search?q="{urllib.parse.quote(title)}"&lang=en&country=us&max={m}&apikey={gnews_key}'
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode("utf-8"))
            for i in range(len(data['articles'])):
                context.append(data["articles"][i]['content'])
        time.sleep(1)
        all_contexts.append(context)
    all_str_context=[]
    for context in all_contexts:
        strcontext=""
        for i in context:
            strcontext += i +'\n'
        all_str_context.append(strcontext)
    return all_str_context

@st.cache_data
def generate_questions(background, news):
    client = OpenAI()
    res=[]
    for b, n in zip(background, news):
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a beloved charismatic host of trivia at your local bar.Your job is to ask trivia questions using the context provided and then also provide the correct answer."},
                {"role": "system", "content": "Format your response like Q: question newline A: answer"},
                {"role": "system", "content": "Use this as context for your question:" + b + '\n' + n},
                {"role": "user", "content": "Based on the context, please ask your audience a question and provide the correct answer afterward."},
                {"role": "system", "content": "If your question contains themes of violence, simply respond 'pass' "},
            ]
        )
        print(completion.choices[0].message.content)
        res.append(completion.choices[0].message.content)
    return res

titles, extracts = wiki_trending_today(10)
news = find_corresponding_news(titles, 10, 3)
res =generate_questions(extracts, news)
for QA in res:
    if QA != 'pass':
        question, answer = QA.split('\nA: ')
        with st.expander(f"{question[3:]}"):  # Corrected with an f-string
            st.markdown(f"{answer}")  # Use f-string here as well to display the answer

