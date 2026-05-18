from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_corpus(topic):
    corpus = []
    corpus.append(topic.get("definition", ""))

    for c in topic.get("key_concepts", []):
        corpus.append(f"{c['name']} {c['description']}")

    for t in topic.get("types", []):
        corpus.append(f"{t['type']} {t['description']} {' '.join(t.get('examples', []))}")

    return corpus


def answer_question(question, topic):
    corpus = build_corpus(topic)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus + [question])

    similarity = cosine_similarity(X[-1], X[:-1])
    best_idx = similarity.argmax()
    best_score = similarity[0][best_idx]

    if best_score < 0.2:
        return "I could not find this in the current topic."

    return corpus[best_idx]