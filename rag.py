import json
import os
from types import SimpleNamespace
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from video_link import VIDEO_LINKS

try:
    from google import genai as google_genai
except Exception:
    google_genai = None

# Load Environment Variables

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = None
df = None
embedding_matrix = None


def get_api_key():
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    if API_KEY:
        return API_KEY
    return None


def _load_embeddings():
    global df, embedding_matrix

    if df is not None and embedding_matrix is not None:
        return

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EMBEDDING_PATH = os.path.join(
        BASE_DIR,
        "Embeddings",
        "gemini_embeddings.pkl"
    )

    if not os.path.exists(EMBEDDING_PATH):
        raise FileNotFoundError(f"Embedding file not found: {EMBEDDING_PATH}")

    loaded_df = pd.read_pickle(EMBEDDING_PATH)

    loaded_df = loaded_df[
        loaded_df["embedding"].apply(
            lambda x: isinstance(x, list) and len(x) == 3072
        )
    ].reset_index(drop=True)

    df = loaded_df
    embedding_matrix = np.vstack(df["embedding"].values)


def _post_gemini(path, payload):
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Set it in your environment or Vercel settings.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{path}?key={api_key}"
    print(f"[DEBUG] POST {url}")
    response = requests.post(url, json=payload, timeout=90)
    if not response.ok:
        print(f"[ERROR] Gemini API returned {response.status_code}: {response.text[:500]}")
    response.raise_for_status()
    return response.json()


class RestGeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = self

    def generate_content(self, model, contents):
        prompt = contents if isinstance(contents, str) else contents[0] if isinstance(contents, list) and len(contents) > 0 else str(contents)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        data = _post_gemini(f"{model}:generateContent", payload)
        candidate = data.get("candidates", [{}])[0]
        parts = candidate.get("content", {}).get("parts", [])
        text = parts[0].get("text", "") if parts else ""
        return SimpleNamespace(text=text)

    def embed_content(self, model, contents, config=None):
        text = contents[0] if isinstance(contents, list) and len(contents) > 0 else str(contents)
        payload = {
            "model": f"models/{model}",
            "content": {"parts": [{"text": text}]},
        }
        if config and config.get("task_type"):
            payload["taskType"] = config["task_type"]
        data = _post_gemini(f"{model}:embedContent", payload)
        values = data.get("embedding", {}).get("values", [])
        return SimpleNamespace(embeddings=[SimpleNamespace(values=values)])


def get_client():
    global client

    if client is not None:
        return client

    api_key = get_api_key()
    print(f"Using Gemini API key from environment: {'yes' if api_key else 'no'}")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Set it in your environment or Vercel settings.")

    if google_genai is not None:
        client = google_genai.Client(api_key=api_key)
    else:
        client = RestGeminiClient(api_key)
    return client


FORBIDDEN_TERMS = [
    "sex", "sexual", "nude", "naked", "porn", "explicit", "adult", "xxx",
    "horny", "fuck", "bitch", "dick", "pussy", "boobs", "breasts", "erotic"
]


def is_irrelevant_or_unsafe(question):
    """Only block explicitly inappropriate/unsafe questions.
    All other questions pass through — the embedding similarity score
    and relevance floor (0.30) naturally filter off-topic queries."""
    if not question or not isinstance(question, str):
        return True

    normalized = question.lower().strip()
    if not normalized:
        return True

    if any(term in normalized for term in FORBIDDEN_TERMS):
        return True

    return False

# Embedding Function

def create_query_embedding(question):
    model_client = get_client()

    response = model_client.models.embed_content(
        model="gemini-embedding-001",
        contents=[question],
        config={
            "task_type": "RETRIEVAL_QUERY"
        }
    )

    return response.embeddings[0].values


# Retrieve Relevant Chunks

def retrieve_chunks(question, top_k=15):
    _load_embeddings()
    question_embedding = create_query_embedding(question)

    similarities = cosine_similarity(
        embedding_matrix,
        [question_embedding]
    ).flatten()

    # Create dataframe with similarity scores
    retrieved = df.copy()

    retrieved["similarity"] = similarities

    # Sort by similarity first
    retrieved = retrieved.sort_values(
        "similarity",
        ascending=False
    )

    # Log top similarities for debugging
    top_sims = retrieved["similarity"].head(10).tolist()
    print(f"[DEBUG] Top 10 similarities: {[round(s, 4) for s in top_sims]}")

    # Relevance floor: if the BEST match is below 0.30, the question is
    # completely off-topic (e.g. unrelated to deep learning) — return nothing
    if top_sims and top_sims[0] < 0.30:
        print(f"[INFO] Best similarity {top_sims[0]:.4f} is below relevance floor 0.30. Question is off-topic.")
        return []

    # Filter by threshold
    above_threshold = retrieved[
        retrieved["similarity"] >= 0.45
    ]

    # If nothing passes 0.45 but best is above floor, use top results
    if len(above_threshold) == 0:
        print(f"[WARN] No chunks above 0.45 threshold. Using top {min(5, len(retrieved))} results.")
        above_threshold = retrieved.head(5)

    retrieved = above_threshold.head(top_k)

    print(f"[DEBUG] Retrieved {len(retrieved)} chunks for question: {question[:80]}")

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

✓ If the student's question is NOT about Deep Learning, Neural Networks,
  Machine Learning, AI, or related technical topics, return an EMPTY array: []
  Do NOT try to match unrelated questions to course content.

Return ONLY JSON.
"""


# Gemini Answer Generation

def generate_answer(prompt):
    try:
        model_client = get_client()
        response = model_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response.text:
            print("[WARN] Gemini Response was empty or blocked by safety filters.")
            return []

        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```json"):
            text = text[len("```json"):]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        print(f"[DEBUG] Gemini Response (first 500 chars): {text[:500]}")

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Gemini Response was not valid JSON: {e}")
            print(f"[ERROR] Raw text: {text[:1000]}")
            return []
    except Exception as e:
        print(f"[ERROR] Error generating answer: {e}")
        import traceback
        traceback.print_exc()
        return []


def build_fallback_results(retrieved_chunks):
    fallback_results = []

    for chunk_group in retrieved_chunks:
        try:
            first_chunk = chunk_group["chunks"][0]
            first_timestamp = int(first_chunk.get("start", 0))
        except (IndexError, TypeError, ValueError):
            continue

        fallback_results.append({
            "video_number": int(chunk_group.get("number", 0)),
            "video_title": chunk_group.get("title", "Relevant Video"),
            "timestamps": [
                {
                    "seconds": first_timestamp,
                    "description": "Relevant explanation found in the retrieved transcript chunks."
                }
            ],
            "youtube_url": f"{VIDEO_LINKS.get(int(chunk_group.get('number', 0)), '')}?t={first_timestamp}"
        })

    return fallback_results


# Main Function Called by Flask

def ask_question(question):
    if is_irrelevant_or_unsafe(question):
        print(f"[INFO] Rejected question as irrelevant or unsafe: {question}")
        return []

    print(f"\n[INFO] === Processing question: {question} ===")

    retrieved_chunks = retrieve_chunks(question)

    print(f"[INFO] Retrieved {len(retrieved_chunks)} chunk groups")

    if not retrieved_chunks:
        print("[WARN] No chunks retrieved at all")
        return []

    prompt = build_prompt(question, retrieved_chunks)
    results = generate_answer(prompt)

    if not results or not isinstance(results, list):
        print("[WARN] Gemini returned no valid results, using fallback")
        results = build_fallback_results(retrieved_chunks)

    results = [
        result
        for result in results
        if isinstance(result, dict) and result.get("timestamps") and len(result["timestamps"]) > 0
    ]

    for result in results:
        try:
            first_timestamp = result["timestamps"][0]["seconds"]
            result["youtube_url"] = (
                f"{VIDEO_LINKS.get(result['video_number'], '')}?t={int(first_timestamp)}"
            )
        except (KeyError, IndexError, ValueError) as e:
            print(f"[ERROR] Error building youtube URL for video card: {e}")
            continue

    print(f"[INFO] Returning {len(results)} final results")
    return results
