from dictionary import Offer
from dictionary import process_text
from sklearn.feature_extraction.text import CountVectorizer
from dictionary import stop_spanish
import gensim

KEYSPACES = ['symplicity']
FEATURES = ['Description','Qualifications', 'Software']
NGRAM_RANGE = (1, 1)
MAX_DF = 0.9
MIN_DF = 0.1

def train(documents):
#    model = gensim.models.Word2Vec(documents)
#    print(len(model.wv.vocab))

    all_phrases = []

    cnt_vectorizer = CountVectorizer(stop_words=stop_spanish,
                                     ngram_range=NGRAM_RANGE,
                                     max_df=MAX_DF, min_df=MIN_DF,
                                     )

    analyze = cnt_vectorizer.build_analyzer()

    processed_docs = []
    for doc in documents:
        processed_doc = analyze(doc)
        processed_docs.append(processed_doc)

    model = gensim.models.Word2Vec(processed_docs)
    return model

def save(model):
    model.save('w2v/model')


def get_documents(keyspaces, feature_list):
    documents = []
    for keyspace in keyspaces:
        offers = Offer.SelectAll(keyspace)

        for offer in offers:
            text = ""
            for feature in feature_list:
                if feature in offer.features:
                    text += offer.features[feature] + ' '

            text = process_text(text)
            documents.append(text)

    return documents

def main():
    documents = get_documents(KEYSPACES, FEATURES)
    model = train(documents)
    save(model)

if __name__ == "__main__":
    main()
    print("Fin del entrenamiento!")
