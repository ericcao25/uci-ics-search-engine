import json
import math
from text_tokenizer import tokenize_query
from collections import defaultdict
import time

class SearchEngine:
    def __init__(self, index_path: str, doc_ids_path: str, lexicon_path: str, norms_path: str):
        self.index_path = index_path

        with open(doc_ids_path, "r") as f:
            self.doc_ids = json.load(f)

        with open(lexicon_path, "r") as f:
            self.lexicon = json.load(f)

        with open(norms_path, "r") as f:
            self.norms = json.load(f)
        self.N_docs = len(self.doc_ids)

    def load_postings_for_token(self, token: str) -> dict[str, dict]:
        """Use byte offset from lexicon to jump directly to the postings."""
        if token not in self.lexicon:
            return {}

        offset = self.lexicon[token]

        with open(self.index_path, "r") as f:
            f.seek(offset)              # Jump directly to the JSONL line
            line = f.readline()
            obj = json.loads(line)
            return obj["postings"]

    def search(self, query: str) -> list[tuple[str, float]]:
        """
        Returns a list of (doc_url, score) sorted by descending score.
        Score = sum of tf-idf of all query tokens.
        """
        # Normalize + stem to get tokens
        tokens = tokenize_query(query)
        if not tokens:
            return []
        
        # Uncomment below for searching with no cosine similarity
        # doc_scores = defaultdict(float)

        # for token in tokens:
        #     postings = self.load_postings_for_token(token)
        #     for doc_id, posting in postings.items():
        #         doc_scores[doc_id] += posting.get("tfidf", 0.0)

        # # Rank documents by score
        # ranked_results = sorted(
        #     ((self.doc_ids[doc_id], score) for doc_id, score in doc_scores.items()),
        #     key=lambda x: x[1],
        #     reverse=True
        # )

        # return ranked_results[:5]

        query_tf = defaultdict(int)
        for token in tokens:
            query_tf[token] += 1

        query_weights = {}
        scores = defaultdict(float)
        query_norm_sq = 0
        for token, tf in query_tf.items():
            postings = self.load_postings_for_token(token)
            if not postings:
                continue
            df = len(postings)
            idf = math.log(self.N_docs / df)
            tf_idf = (1 + math.log(tf)) * idf
            query_weights[token] = tf_idf
            query_norm_sq += tf_idf * tf_idf

            for doc_id, posting in postings.items():
                scores[doc_id] += posting.get("tfidf", 0.0) * tf_idf

        query_norm = math.sqrt(query_norm_sq)
        if query_norm == 0:
            return []
        
        doc_scores = {}
        for doc_id, score in scores.items():
            doc_norm = self.norms[doc_id]
            if doc_norm > 0:
                doc_score = (score / query_norm) / doc_norm
                doc_scores[doc_id] = doc_score

        # Rank documents by score
        ranked_results = sorted(
            ((self.doc_ids[doc_id], score) for doc_id, score in doc_scores.items()),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked_results[:5]
