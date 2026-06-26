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

    question = request.json["question"]

    answer = ask_question(question)

    return jsonify({

    "results": answer

})


if __name__ == "__main__":
    app.run(debug=True)