import re
from better_profanity import profanity

def load_badwords(filepath="vn_offensive_words.txt"):
    badwords = []
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            term = line.strip().lower()
            if term and not term.startswith('#'):
                badwords.append(term)
    return badwords

BADWORDS_VI = load_badwords()
profanity.load_censor_words()

def contains_bad_word(text, badwords=BADWORDS_VI):
    text = re.sub(r"[^\w\s]", "", text.lower())
    for word in badwords:
        if re.search(rf'\b{re.escape(word)}\b', text):
            return True
    return False

def check_content(text):
    # Check tiếng Anh
    if profanity.contains_profanity(text):
        return True
    # Check tiếng Việt
    if contains_bad_word(text):
        return True
    return False