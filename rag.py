import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
from sklearn.metrics.pairwise import cosine_similarity
from video_link import VIDEO_LINKS

# Load Environment Variables

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")

# Gemini Client (Load Once)

client = genai.Client(api_key=API_KEY)

# Load Embeddings Once

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMBEDDING_PATH = os.path.join(
    BASE_DIR,
    "Embeddings",
    "gemini_embeddings.pkl"
)

df = pd.read_pickle(EMBEDDING_PATH)

# Remove invalid embeddings only once
df = df[
    df["embedding"].apply(
        lambda x: isinstance(x, list) and len(x) == 3072
    )
].reset_index(drop=True)

embedding_matrix = np.vstack(df["embedding"].values)

# Embedding Function

def create_query_embedding(question):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[question],
        config={
            "task_type": "RETRIEVAL_QUERY"
        }
    )

    return response.embeddings[0].values


# Retrieve Relevant Chunks

def retrieve_chunks(question, top_k=15):

    question_embedding = create_query_embedding(question)

    similarities = cosine_similarity(
        embedding_matrix,
        [question_embedding]
    ).flatten()

    # Create dataframe with similarity scores
    retrieved = df.copy()

    retrieved["similarity"] = similarities

    # Keep only sufficiently similar chunks
    retrieved = retrieved[
        retrieved["similarity"] >= 0.65
    ]

    # Sort by similarity
    retrieved = retrieved.sort_values(
        "similarity",
        ascending=False
    ).head(top_k)

    # Create YouTube URLs
    retrieved["youtube_url"] = retrieved.apply(
        lambda row: f"{VIDEO_LINKS.get(int(row['number']), '')}?t={int(row['start'])}",
        axis=1
    )

    grouped = []

    for video_number, group in retrieved.groupby("number"):

        group = group.sort_values("start")

        grouped.append({

            "number": int(video_number),

            "title": group.iloc[0]["title"],

            "youtube_url": group.iloc[0]["youtube_url"],

            "chunks": group[
                ["start", "end", "text"]
            ].to_dict("records")

        })

    return grouped

# Prompt Builder

def build_prompt(question, retrieved_chunks):

    return f"""
You are an AI assistant for a Deep Learning course.

The Python retrieval system has ALREADY identified the most relevant videos.

Each object below represents ONE UNIQUE video.

Each video already contains ALL relevant transcript chunks for that video.

Question:
"{question}"

Retrieved Videos:
{json.dumps(retrieved_chunks, indent=2)}

--------------------------------------------------

YOUR TASK

For EACH video:

1. Read every transcript chunk.
2. Ignore transcript repetition.
3. Merge related chunks together.
4. Produce ONE response object per video.
5. Keep the timestamps in chronological order.
6. Write concise descriptions in your own words.
7. Do NOT copy transcript text.
8. If two nearby timestamps explain the same idea, merge them into one timestamp.
9. Ignore transcript chunks that are irrelevant to the user's question.

--------------------------------------------------

VERY IMPORTANT

• NEVER create two objects with the same video_number.

• There must be EXACTLY ONE object per video.

• Do NOT invent videos.

• Do NOT invent timestamps.

• Use ONLY the supplied transcript chunks.

• Preserve timestamp accuracy.

--------------------------------------------------

Return ONLY valid JSON.

Format:

[
  {{
    "video_number": 4,
    "video_title": "What is a Perceptron",
    "timestamps": [
      {{
        "seconds": 758,
        "description": "Introduces the Perceptron concept."
      }},
      {{
        "seconds": 1457,
        "description": "Explains how the Perceptron works mathematically."
      }},
      {{
        "seconds": 1863,
        "description": "Shows the geometric interpretation."
      }}
    ]
  }}
]

--------------------------------------------------

QUALITY RULES

✓ Prefer fewer high-quality timestamps over many repetitive ones.

✓ If three timestamps explain exactly the same concept,
keep only the best timestamp.

✓ If several consecutive chunks belong to one explanation,
merge them into a single timestamp.

✓ Descriptions should be 8–15 words.

✓ Rank videos from most relevant to least relevant.

✓ If a video contains NO relevant explanation,
DO NOT include it.

✓ Every returned video MUST contain at least one timestamp.

✓ Never return:

{{
    "video_number": 4,
    "timestamps": []
}}

✓ If no timestamp exists, omit that video completely.

✓ Return at most 8 videos.
Return ONLY JSON.
"""


# Gemini Answer Generation

import json

def generate_answer(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Check if the response was blocked or has no text
        if not response.text:
            print("\nGemini Response was empty or blocked by safety filters.")
            return []
            
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        print("\nGemini Response:\n")
        print(text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print("\nGemini Response was not valid JSON.")
            return []
    except Exception as e:
        print(f"\nError generating answer: {e}")
        return []


# Main Function Called by Flask

def ask_question(question):
    try:
        retrieved_chunks = retrieve_chunks(question)
    except Exception as e:
        print(f"\nError retrieving chunks (possibly due to embedding block): {e}")
        return []

    print("\nRetrieved Chunks:")
    import pprint
    pprint.pp(retrieved_chunks)

    # If no chunks are retrieved, we don't even need to call Gemini
    if not retrieved_chunks:
        return []

    prompt = build_prompt(question, retrieved_chunks)
    results = generate_answer(prompt)

    # In case generate_answer returned an empty list due to an exception/safety block
    if not results or not isinstance(results, list):
        return []

    # Remove videos that have no timestamps
    results = [
        result
        for result in results
        if isinstance(result, dict) and result.get("timestamps") and len(result["timestamps"]) > 0
    ]

    for result in results:
        try:
            first_timestamp = result["timestamps"][0]["seconds"]
            result["youtube_url"] = (
                f"{VIDEO_LINKS[result['video_number']]}?t={int(first_timestamp)}"
            )
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error building youtube URL for video card: {e}")
            continue

    return results