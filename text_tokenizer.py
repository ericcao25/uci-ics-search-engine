'''
text_tokenizer.py

Responsible for turning raw text into normalized tokens.
'''

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import re
from parser import load_document


for pkg in ("punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)


def tokenize_html(html_text: str) -> list[tuple[str, str]]:
    BLACKLIST = {"script", "style", "noscript", "template", "svg"}
    soup = BeautifulSoup(html_text, "html.parser")
    stemmer = PorterStemmer()
    token_field_pairs = []

    for text_node in soup.find_all(string=True):
        text = text_node.strip()
        if not text:
            continue
        tag = text_node.parent.name.lower()
        if tag in BLACKLIST or not re.match(r"^[a-z0-9]+$", tag):
            continue
        raw_tokens = word_tokenize(text.lower())
        for tok in raw_tokens:
            if not re.match(r"^[a-z0-9]+$", tok):
                continue
            stemmed = stemmer.stem(tok)
            token_field_pairs.append((stemmed, tag))

    return token_field_pairs

def tokenize_query(query: str) -> list[str]:
    query = query.lower()
    query_tokens = word_tokenize(query)
    filtered_tokens = [t for t in query_tokens if re.match(r"^[a-z0-9]+$", t)]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(t) for t in filtered_tokens]

    return stemmed_tokens

if __name__ == '__main__':
    # For testing:
    url, content = load_document('DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json')

    tokens = tokenize_html(content)

    print(tokens)