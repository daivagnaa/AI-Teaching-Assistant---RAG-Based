import requests
import os
import json
import pandas as pd

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


jsons = os.listdir("jsons")

my_dicts = []
chunk_id = 0

for json_file in jsons:

    print(f"\nCreating Embeddings for {json_file}")

    with open(
        f"jsons/{json_file}",
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    texts = [c["text"] for c in content["chunks"]]

    embeddings = []

    total_batches = (len(texts) - 1) // BATCH_SIZE + 1

    for i in range(0, len(texts), BATCH_SIZE):

        batch = texts[i:i + BATCH_SIZE]

        print(
            f"Embedding Batch "
            f"{i // BATCH_SIZE + 1}/{total_batches}"
        )

        try:
            batch_embeddings = create_embedding(batch)
            embeddings.extend(batch_embeddings)

        except Exception as e:

            print(
                f"Error in batch "
                f"{i // BATCH_SIZE + 1}: {e}"
            )

            # Fallback to one-by-one embedding
            print("Trying chunk-by-chunk embedding...")

            for text in batch:

                try:
                    single_embedding = create_embedding([text])
                    embeddings.append(single_embedding[0])

                except Exception as chunk_error:

                    print(
                        f"Failed chunk: {chunk_error}"
                    )

                    # Dummy embedding to preserve indexing
                    embeddings.append(None)

    if len(embeddings) != len(content["chunks"]):

        print(
            f"WARNING: Embedding count mismatch "
            f"for {json_file}"
        )

        continue

    for i, chunk in enumerate(content["chunks"]):

        chunk["chunk_id"] = chunk_id
        chunk["embedding"] = embeddings[i]

        my_dicts.append(chunk)

        chunk_id += 1

print("\nCreating DataFrame...")

df = pd.DataFrame.from_records(my_dicts)

print(df.head())
print(f"\nTotal Records: {len(df)}")

# Save for later use
df.to_pickle("embeddings.pkl")

print("\nSaved embeddings.pkl")