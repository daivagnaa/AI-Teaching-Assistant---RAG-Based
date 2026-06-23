import requests
import os
import json
import pandas as pd

def create_embedding(text_list):
    r = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        },
        timeout=300
    )

    r.raise_for_status()

    return r.json()["embeddings"]


BATCH_SIZE = 32

texts = [c["text"] for c in content["chunks"]]

embeddings = []

for i in range(0, len(texts), BATCH_SIZE):

    batch = texts[i:i+BATCH_SIZE]

    print(
        f"Embedding batch "
        f"{i//BATCH_SIZE + 1}/"
        f"{(len(texts)-1)//BATCH_SIZE + 1}"
    )

    batch_embeddings = create_embedding(batch)

    embeddings.extend(batch_embeddings)

jsons = os.listdir("jsons")  # List all the jsons 
my_dicts = []
chunk_id = 0

for json_file in jsons:
    with open(f"jsons/{json_file}") as f:
        content = json.load(f)
    print(f"Creating Embeddings for {json_file}")
    embeddings = create_embedding([c['text'] for c in content['chunks']])
       
    for i, chunk in enumerate(content['chunks']):
        chunk['chunk_id'] = chunk_id
        chunk['embedding'] = embeddings[i]
        chunk_id += 1
        my_dicts.append(chunk) 
# print(my_dicts)

df = pd.DataFrame.from_records(my_dicts)
print(df)
# a = create_embedding(["Cat sat on the mat", "Harry dances on a mat"])
# print(a)