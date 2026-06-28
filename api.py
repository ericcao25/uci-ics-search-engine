from flask import Flask, request, jsonify
from flask_cors import CORS
from search.search_engine import SearchEngine

app = Flask(__name__)
CORS(app)
engine = SearchEngine("data/inverted_index.jsonl", "data/doc_ids.json", "data/lexicon.json", "data/norms.json")

@app.get("/search")
def search():
    query = request.args.get("q", "")
    results = engine.search(query)

    return jsonify([
        {"url": url, "score": score} for url, score in results
    ])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
