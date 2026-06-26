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

    indices = similarities.argsort()[-top_k:][::-1]

    retrieved = df.iloc[indices]

    return retrieved[
        [
            "number",
            "title",
            "start",
            "end",
            "text"
        ]
    ]


# Prompt Builder

def build_prompt(question, retrieved_chunks):

    return f"""
You are an AI assistant helping students navigate a Deep Learning course.

Below are video transcript chunks. Each chunk contains:
- video_number
- video_title
- start (seconds)
- end (seconds)
- transcript text

Video Chunks:
{retrieved_chunks.to_json(orient="records")}

--------------------------------------------------

Student Question:

"{question}"

Your task:

1. Find all transcript chunks that are relevant to the student's question.
2. Match using semantic meaning, not just exact keyword matching.
3. Include synonyms and related concepts whenever appropriate.
4. Group results by video.
5. For each relevant video provide:
   - Video Number
   - Video Title
   - Timestamp in MM:SS format
   - Short description (5-15 words)
6. Merge nearby chunks belonging to the same explanation.
7. If only briefly mentioned, write "Brief mention".
8. Rank from most relevant to least relevant.

Output format:

Your question, "{question}" is covered in the following videos:

Video <number> – <title>
• MM:SS — <short description>

Video <number> – <title>
• MM:SS — <short description>

Rules:
- Keep response under 120 words.
- Do not invent timestamps.
- Use only supplied transcript chunks.
- Convert seconds to MM:SS.
- If nothing relevant exists respond exactly:
No content found.
- No introductory text.
"""



# Gemini Answer Generation

def generate_answer(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# Main Function Called by Flask

def ask_question(question):

    retrieved_chunks = retrieve_chunks(question)

    prompt = build_prompt(
        question,
        retrieved_chunks
    )

    answer = generate_answer(prompt)

    return answer
