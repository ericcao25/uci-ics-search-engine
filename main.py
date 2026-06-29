import os
import nltk
from index.index_builder import build_index
from search.search_engine import SearchEngine
import time

if __name__ == "__main__":
    nltk.download("punkt", quiet=True)

    INDEX_PATH = "data/inverted_index.jsonl"
    IDS_PATH = "data/doc_ids.json"
    LEXICON_PATH = "data/lexicon.json"
    NORMS_PATH = "data/norms.json"

    if any(not os.path.exists(p) for p in ["data", INDEX_PATH, IDS_PATH, LEXICON_PATH, NORMS_PATH]):
        dev_dir = os.path.join(os.getcwd(), "DEV")
        build_index(dev_dir)

    engine = SearchEngine(INDEX_PATH, IDS_PATH, LEXICON_PATH, NORMS_PATH)

    while True:
        #  to run on web instead of console run python3 api.py and then inside of cs121-search folder
        #  run npm run start to start local host (after index is built)
        query = input("Enter search query (blank to exit): ").strip()
        if not query:
            break
        
        start = time.perf_counter()
        results = engine.search(query)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        print(f"\nSearch took {elapsed_ms:.2f} ms")
        
        print("\nTop results:")
        for i, (url, score) in enumerate(results):
            print(f'{i+1}. {url}')
        print()
