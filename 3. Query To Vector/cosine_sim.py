import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests

df = pd.read_csv("embeddings.csv")

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "bge-m3"
BATCH_SIZE = 16

def create_embedding(text_list):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "input": text_list
        },
        timeout=300
    )

    r.raise_for_status()

    response = r.json()

    if "embeddings" not in response:
        raise Exception(
            f"Embeddings not found in response.\nResponse: {response}"
        )

    return response["embeddings"]

question = input("Enter your question: ")
question_embedding = create_embedding([question])[0]


# Find similarities of question embeddings with other embeddings
# print(np.vstack(df['embedding'].values))
# print(np.vstack(df['embedding'].values).shape)
similarities = cosine_similarity(np.vstack(df['embedding'].values), [question_embedding]).flatten()
print(f"For question '{question}', similarities with existing embeddings: {similarities}")
print(f"Indices of top 5 most similar embeddings: {similarities.argsort()[-5:][::-1]}")  # Print indices of top 5 most similar embeddings

new_df = df.iloc[similarities.argsort()[-5:][::-1]]
dff = new_df[['number', 'title', 'start', 'end', 'text']]