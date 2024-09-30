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


st.write("wiki_key", st.secrets["wiki_key"])


st.title('Trivia Questions For Right Now')
today = datetime.datetime.now()
date = today.strftime('%Y/%m/%d')

language_code = 'en' # English
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
links=[]
for i in response['mostread']['articles'][:2]:
    if 'description' in i.keys():
       titles.append(i['titles']['normalized'])
       extracts.append(i['extract'])
       links.append(i)

st.text(titles)


gnews_key=st.secrets["gnews_key"]
all_contexts=[]

for title in titles:
    context=[]
    print(title)
    url = f'https://gnews.io/api/v4/search?q="{urllib.parse.quote(title)}"&lang=en&country=us&max=10&apikey={gnews_key}'
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read().decode("utf-8"))
        articles = data["articles"]
        if len(articles) > 3:
            print(articles[0]['content'])
            context.append(articles[0]['content'])
            context.append(articles[1]['content'])
            context.append(articles[2]['content'])
            all_contexts.append(context)
    st.text(context)
    time.sleep(1)


all_str_context=[]
for context in all_contexts:
    strcontext=""
    for i in context:
        strcontext +=i +'\n'
    all_str_context.append(strcontext)

client = OpenAI()
res=[]
for c in all_str_context:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a beloved charismatic host of trivia at your local bar.Your job is to ask trivia questions using the context provided and then also provide the correct answer."},
            {"role": "system", "content": "Format your response like Q: question A: answer"},
            {"role": "system", "content": "If the content of the context includes violence, simply respond 'pass' "},

            {"role": "system", "content": c},
            {
                "role": "user",
                "content": "Based on the context, please ask your contestants a Jeopardy!-style question and also provide the correct answer afterward."
            }
        ]
    )
    res.append(completion.choices[0].message.content)

    st.text(completion.choices[0].message.content)

# DATE_COLUMN = 'date/time'
# DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
#             'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

# @st.cache_data
# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data

# data_load_state = st.text('Loading data...')
# data = load_data(10000)
# data_load_state.text("Done! (using st.cache_data)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)

# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)
