import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load Environment Variables
# -----------------------------

# Load environment variables
load_dotenv()

def get_api_key():
    """Get API key from environment variables"""
    # Try GEMINI_API_KEY first
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    return None
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
api_key = get_api_key()
if not api_key:
    raise ValueError("API key not found. Please check your .env file.")

# -----------------------------
# Load Embeddings
# -----------------------------
df = pd.read_pickle(
    r"E:\Data Science\Projects\AI Teaching Assistant\gemini_embeddings.pkl"
)

# -----------------------------
# Gemini Query Embedding
# -----------------------------
def create_query_embedding(question):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[question],
        config={
            "task_type": "RETRIEVAL_QUERY"
        }
    )

    return response.embeddings[0].values


# -----------------------------
# User Question
# -----------------------------
question = input("Enter your question: ")

question_embedding = create_query_embedding(question)

# -----------------------------
# Cosine Similarity
# -----------------------------
# Remove invalid embeddings
df = df[df["embedding"].apply(lambda x: isinstance(x, list) and len(x) == 3072)].reset_index(drop=True)

similarities = cosine_similarity(
    np.vstack(df["embedding"].values),
    [question_embedding]
).flatten()
# print(f"For question '{question}', similarities with existing embeddings: {similarities}")
# print(f"Indices of top 5 most similar embeddings: {similarities.argsort()[-5:][::-1]}")  # Print indices of top 5 most similar embeddings

new_df = df.iloc[similarities.argsort()[-5:][::-1]]
dff = new_df[['number', 'title', 'start', 'end', 'text']]

prompt = f"""
You are an AI assistant helping students navigate a Deep Learning course.

Below are video transcript chunks. Each chunk contains:
- video_number
- video_title
- start (seconds)
- end (seconds)
- transcript text

Video Chunks:
{dff.to_json(orient="records")}

--------------------------------------------------

Student Question:
"{question}"

Your task:

1. Find all transcript chunks that are relevant to the student's question.
2. Match using semantic meaning, not just exact keyword matching.
   - Include synonyms and related concepts whenever appropriate.
3. Group results by video.
4. For each relevant video, provide:
   - Video Number
   - Video Title
   - Timestamp in MM:SS format
   - A very short description (5–15 words) of what is explained there.
5. Rank results from most relevant to least relevant.
6. If multiple nearby chunks belong to the same explanation, merge them into one timestamp range.
7. If only a brief mention exists, explicitly state "Brief mention".
8. If a concept is explained in depth across multiple timestamps in the same video, mention each important section.

Output format:

Your question, "{question}" is covered in the following videos:

Video <number> – <title>
• MM:SS — <short description with your own words dont just copy the transcript>

Video <number> – <title>
• MM:SS — <short description with your own words dont just copy the transcript>

continue for all relevant videos.

Rules:
- Keep the response under 120 words.
- Do not use end time in the output.
- Do not invent timestamps or explanations.
- Only use the provided transcript chunks.
- Convert starting seconds to MM:SS format.
- If no relevant content exists, respond exactly:
No content found
- Do not ask follow-up questions.
- Do not add introductory or concluding text.
"""

promptt = f"""
Video transcript chunks:
{dff.to_json(orient="records")}

Question: "{question}"

Find all chunks relevant to the question (semantic match, not just keywords).

Return only:
The Relevant Videos for your question, "{question}"
Video <number> - <title>
• MM:SS — <short description with your own words dont just copy the transcript>


Group nearby chunks from the same video. Sort by relevance. Convert starting seconds to MM:SS. Use only the given data. If no relevant chunk exists, reply exactly:
No content found, do not use words like chunk, section, or part instead use word "video". Do not invent timestamps or explanations.
"""

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)