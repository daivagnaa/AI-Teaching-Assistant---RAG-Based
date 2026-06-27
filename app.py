from flask import Flask, render_template, request, jsonify
from rag import ask_question

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/search")
def search():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.json.get("question", "")
        if not question:
            return jsonify({"results": []})
        answer = ask_question(question)
        return jsonify({"results": answer})
    except Exception as e:
        print(f"Server error in /ask: {e}")
        return jsonify({"results": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    #     app.run(debug=True)