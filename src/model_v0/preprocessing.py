
from nltk.tokenize import word_tokenize


MAX_TOKEN_LENGTH = 50

def preprocess_input_text(input_text: str) -> str:
    tokenizedWords = word_tokenize(input_text)
    tokenized_text = [token.lower() for token in tokenizedWords]
    processed_text = " ".join(tokenized_text[:MAX_TOKEN_LENGTH])
    return processed_text