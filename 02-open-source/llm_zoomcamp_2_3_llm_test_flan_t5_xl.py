# -*- coding: utf-8 -*-
"""LLM Zoomcamp 2.3 - llm-test-flan-t5-xl.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RzIy5N-YACXpe52USTVzoPx2rPJ1eAGD

[LLM Zoomcamp 2.3 - HuggingFace and Google FLAN T5
](https://www.youtube.com/watch?v=a86iTyxnFE4&list=PL3MmuxUbc_hIB4fSqLy_0AfTjVLpgjV3R&index=10)
"""

!wget https://raw.githubusercontent.com/alexeygrigorev/minsearch/main/minsearch.py

!pip install -U transformers accelerate bitsandbytes

!nvidia-smi

from transformers import T5ForConditionalGeneration, T5Tokenizer

model_name = "google/flan-t5-xl"

model = T5ForConditionalGeneration.from_pretrained(model_name, device_map="auto")
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
tokenizer.model_max_length = 4096

input_text = "translate English to German: How old are you?"
input_ids = tokenizer(input_text, return_tensors='pt').input_ids.to("cuda")
input_ids

outputs = model.generate(input_ids)
print(tokenizer.decode(outputs[0]))

import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device



import requests

docs_url = 'https://github.com/alexeygrigorev/llm-rag-workshop/raw/main/notebooks/documents.json'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)


import minsearch

index = minsearch.Index(
    text_fields=["question", "text", "section"],
    keyword_fields=["course"]
)

index.fit(documents)

def retrieve_documents(query):
    filter_dict = {"course": "data-engineering-zoomcamp"}
    boost_dict = {"question": 3}

    results = index.search(query, filter_dict, boost_dict, num_results=5)

    return results

def build_context(documents):
    context = ""

    for doc in documents:
        doc_str = f"{doc['question']}\n{doc['text']}\n\n"
        context += doc_str

    context = context.strip()
    return context


def build_prompt(user_question, documents):
    context = build_context(documents)
    return f"""
Question: {user_question}

Context:

{context}

Answer:
""".strip()

def ask_model(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    outputs = model.generate(input_ids, max_length=100)
    answers = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    return answers[0]

def qa_bot(user_question):
    context_docs = retrieve_documents(user_question)
    prompt = build_prompt(user_question, context_docs)

    print(f"\nprompt: {prompt}\n")
    answer = ask_model(prompt)
    return answer

qa_bot('I just discovered the couse. can i still enrol')

user_question = 'I just discovered the couse. can i still enrol'
context_docs = retrieve_documents(user_question)
prompt = build_prompt(user_question, context_docs)

print(prompt)

