from flask import Flask, render_template, request, jsonify
import os
import traceback

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/search")
def search():
    return render_template("index.html")


@app.route("/debug")
def debug():
    """Debug endpoint to verify Vercel deployment health."""
    info = {}

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    info["api_key_set"] = bool(api_key)
    info["api_key_length"] = len(api_key) if api_key else 0
    info["api_key_preview"] = f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else "too short or missing"

    # Check embedding file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    emb_path = os.path.join(base_dir, "Embeddings", "gemini_embeddings.pkl")
    info["embedding_file_exists"] = os.path.exists(emb_path)
    if os.path.exists(emb_path):
        info["embedding_file_size_mb"] = round(os.path.getsize(emb_path) / (1024 * 1024), 2)

    # Check if google-genai is importable
    try:
        from google import genai as google_genai
        info["google_genai_available"] = True
    except Exception as e:
        info["google_genai_available"] = False
        info["google_genai_error"] = str(e)

    # Check if requests is available
    try:
        import requests
        info["requests_available"] = True
    except Exception:
        info["requests_available"] = False

    # Check numpy/pandas/sklearn
    try:
        import numpy
        info["numpy_available"] = True
    except Exception:
        info["numpy_available"] = False
    try:
        import pandas
        info["pandas_available"] = True
    except Exception:
        info["pandas_available"] = False

    info["base_dir"] = base_dir
    info["cwd"] = os.getcwd()

    return jsonify(info)


@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.json.get("question", "")
        if not question:
            return jsonify({"results": [], "error": "No question provided"})

        from rag import ask_question

        answer = ask_question(question)
        return jsonify({"results": answer, "error": None})
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        tb = traceback.format_exc()
        print(f"[CRITICAL] Server error in /ask: {error_msg}")
        print(f"[CRITICAL] Traceback:\n{tb}")
        return jsonify({"results": [], "error": error_msg})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)