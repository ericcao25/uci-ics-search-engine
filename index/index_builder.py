'''
index_builder.py

Responsible for building and storing the inverted index.
'''
import os
import json
from pympler import asizeof
from parser import load_document
from text_tokenizer import tokenize_html
from index.merge_indices import combine_partial_indices

class Posting:
    def __init__(self):
        self.tf = 1
        #Use a dictionary to store each field with its respective count
        self.field_counts = {}   # key = field, value = count of occurrences

    def add_field(self, field):
        #Adds new field; If field exists, increment TF by 1
        self.field_counts[field] = self.field_counts.get(field, 0) + 1

    def increaseTF(self):
        self.tf += 1

    def __repr__(self):
        return f"Posting(tf={self.tf}, fields={self.field_counts})"


class InvertedIndex:
    def __init__(self):
        self.doc_ids = {}          # doc_id --> url
        self.url_to_id = {}        # url --> doc_id
        self.postings = {}         # token --> {doc_id --> Posting}
        self.next_id = 0

    def add_document(self, url: str, tokens: list[tuple[str, str]]) -> None:
        """
        Add a document's tokens to the inverted index
        """
        # Assign a unique doc ID for this URL if not already assigned
        if url not in self.url_to_id:
            doc_id = self.next_id
            self.url_to_id[url] = doc_id
            self.doc_ids[doc_id] = url
            self.next_id += 1
        else:
            doc_id = self.url_to_id[url]

        # Update the inverted index for each token
        for token, field in tokens:

            # If token is new, create a postings dict for it
            if token not in self.postings:
                self.postings[token] = {}

            # If this document has never seen this token
            if doc_id not in self.postings[token]:
                posting = Posting()
                posting.add_field(field)
                self.postings[token][doc_id] = posting

            # If the token already exists for this document
            else:
                posting = self.postings[token][doc_id]
                posting.increaseTF()            
                posting.add_field(field)      #Increment TF for respective field  
        
    def num_documents(self):
        return len(self.doc_ids)

    def num_tokens(self):
        return len(self.postings)
    
    def save_doc_ids(self, doc_ids_path: str):
        """
        Save the doc_ids to disk as a JSON file.
        """
        with open(doc_ids_path, "w") as f:
            json.dump(self.doc_ids, f)

    def save_index(self, index_path: str):
        """
        Saves the inverted index to disk as a JSONL file.
        Each line of this file represents a token's postings.
        """
        with open(index_path, "w") as f:
            for token in sorted(self.postings.keys()):
                postings_dict = {doc_id: vars(p) for doc_id, p in self.postings[token].items()}
                line = {"token": token, "postings": postings_dict}
                f.write(json.dumps(line) + "\n")

    def clear(self):
        self.postings = {}
     
    def size_kb(self, path: str) -> float:
        """
        Return the size (KB) of the saved index file on disk.
        """
        size_bytes = os.path.getsize(path)
        return size_bytes / 1024

def walk_json_files(root_dir: str):
    """Yield absolute file paths for every JSON file under root_dir."""
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                yield os.path.join(root, file)

def build_index(dev_dir: str):
    """Coordinates the full indexing pipeline and saves it into partial indices."""
    index = InvertedIndex()
    file_count = 1
    MAX_INDEX_SIZE = 50000 * 1024 * 13
    if not os.path.exists('data'):
        os.mkdir('data')

    for file_path in walk_json_files(dev_dir):
        print(file_path)
        url, content = load_document(file_path)  # parse JSON from file --> text
        tokens = tokenize_html(content)               # parse text --> normalized tokens
        index.add_document(url, tokens)          # build inverted index

        # save index to disk if needed
        if (index.next_id % 1000 == 0):
            if asizeof.asizeof(index) > MAX_INDEX_SIZE:
                index.save_index(f"data/partial_index{file_count}.jsonl")
                index.clear()
                file_count += 1
    index.save_doc_ids("data/doc_ids.json")
    index.save_index(f"data/partial_index{file_count}.jsonl")
    partial_indices_files = [f"data/partial_index{i}.jsonl" for i in range(1, file_count+1)]
    combine_partial_indices(partial_indices_files, "data/inverted_index.jsonl", "data/lexicon.json", "data/norms.json", index.num_documents())
    print('\nIndex created successfully\n')