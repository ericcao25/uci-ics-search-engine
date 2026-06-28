import heapq
import json
import math
from collections import defaultdict

def combine_partial_indices(partials: list[str], index_file: str, lexicon_file: str, norms_file: str, N_docs: int):
    """Merges partial indexes into one index"""

    fps = [open(f, "r") for f in partials]
    heap = initialize_heap(fps)
    lexicon = {}
    norms = defaultdict(float)

    with open(index_file, "w") as out:
        merge_and_write(out, fps, heap, lexicon, norms, N_docs)

    write_lexicon(lexicon_file, lexicon)
    write_norms(norms_file, norms)
    close_all(fps)


def initialize_heap(fps):
    heap = []
    for i, fp in enumerate(fps):
        line = fp.readline()
        if line:
            obj = json.loads(line)
            heapq.heappush(heap, (obj["token"], i, obj))
    return heap


def merge_and_write(out, fps, heap, lexicon, norms, N_docs):
    current_token = None
    combined = {}

    while heap:
        token, file_id, obj = heapq.heappop(heap)

        # First token
        if current_token is None:
            current_token = token

        # New token encountered --> write previous postings
        if token != current_token:
            write_token_entry(out, current_token, combined, lexicon, norms, N_docs)
            current_token = token
            combined = {}

        merge_postings(combined, obj["postings"])

        push_next_line(file_id, fps, heap)

    # End of heap --> write last token's postings
    if current_token is not None:
        write_token_entry(out, current_token, combined, lexicon, norms, N_docs)


def write_token_entry(out, token, postings, lexicon, norms, N_docs):
    df = len(postings)
    idf = math.log(N_docs / df)

    FIELD_WEIGHTS = {
        "title": 3.0,
        "h1": 2.5,
        "h2": 2.0,
        "h3": 1.5,
        "b": 1.2,
    }

    # For each posting, compute tf-idf with weighted tf for important words
    for doc_id, posting in postings.items():
        weighted_tf = sum(freq * FIELD_WEIGHTS.get(field, 1.0) for field, freq in posting["field_counts"].items())
        tf = 1 + math.log(weighted_tf) if weighted_tf > 0 else 0
        posting["tfidf"] = tf * idf
        norms[doc_id] += tf * idf * tf * idf

    offset = out.tell()
    lexicon[token] = offset
    out.write(json.dumps({"token": token, "postings": postings}) + "\n")


def merge_postings(dst, src):
    for doc_id, posting in src.items():
        if doc_id not in dst:
            dst[doc_id] = posting
        else:
            # IMPORTANT: if Posting has more fields, must store them here
            dst[doc_id]["tf"] += posting["tf"]
            for field, freq in posting["field_counts"].items():
                dst[doc_id]["field_counts"][field] = dst[doc_id]["field_counts"].get(field, 0) + freq


def push_next_line(file_id, fps, heap):
    line = fps[file_id].readline()
    if line:
        obj = json.loads(line)
        heapq.heappush(heap, (obj["token"], file_id, obj))


def write_lexicon(path, lexicon):
    with open(path, "w") as f:
        json.dump(lexicon, f, indent=2)

def write_norms(path, norms):
    for doc_id, norm in norms.items():
        norms[doc_id] = math.sqrt(norm)
    with open(path, "w") as f:
        json.dump(norms, f, indent=2)

def close_all(fps):
    for fp in fps:
        fp.close()