'''
parser.py

Responsible for loading and extracting raw text from the dataset files.
'''

import json

def load_document(file_path: str) -> tuple[str, str]:
    with open(file_path, 'r') as f:
        data = json.load(f)

    return data["url"], data["content"]