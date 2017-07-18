from dictionary import interface
from dictionary import init_fail
from dictionary import Offer
from dictionary import Document
from dictionary import Phrase
from sklearn.feature_extraction.text import CountVectorizer
from dictionary import stop_spanish
import gensim
import numpy


def get_documents(keyspaces, feature_list):
    documents = []
    for keyspace in keyspaces:
        # Find something better
        if not Offer.BuildPreparedStatements(keyspace):
            return None
        offers = Offer.SelectAll(keyspace)

        for offer in offers:
            text = ""
            for feature in feature_list:
                if feature in offer.features:
                    text += offer.features[feature] + ' '

            documents.append(Document(text,keyspace))
                
    return documents


def get_phrases(documents, ngrams, dfs, dictionary):
    stopwords = dictionary.all_phrases() + stop_spanish
    min_ngrams = ngrams[0]
    max_ngrams = ngrams[1]

    min_df = dfs[0]
    max_df = dfs[1]

    cnt_vectorizer = CountVectorizer(stop_words = stopwords,
                                     ngram_range=(min_ngrams, max_ngrams),
                                     max_df = max_df, min_df = min_df,
                                     )
    texts = []
    for doc in documents:
        txt = doc.process_text()
        texts.append(txt)

    terms_matrix = cnt_vectorizer.fit_transform(texts)
    terms_per_document = cnt_vectorizer.inverse_transform(terms_matrix)

    phrases = get_comparable_phrases(terms_per_document, documents)
    return phrases


def get_comparable_phrases(terms_per_document, documents):
    phrases = {}
    for idx, doc in enumerate(terms_per_document):
        for term in doc:
            if term not in phrases:
                #Initialize a 2 lenght list [cnt, source]
                phrases[term] = [0, documents[idx].source]

            # Increase cnt
            phrases[term][0] += 1

    print(len(phrases))

    # Build model phrases
    comparable_phrases = []
    for phrase, values in phrases.items():
        comp_phrase = Phrase(None, phrase, [], values[0], values[1])
        comparable_phrases.append(comp_phrase)

    return comparable_phrases


def get_word2vec():
    model = gensim.models.Word2Vec.load('w2v/model')
    print(model.most_similar(positive=['excel']))
    return model
    
def get_similars(phrases, model):
    phrases.sort()

    for idx, phrase in enumerate(phrases):
        for next_phrase in phrases[idx:]:
            if model.wv.similarity(phrase.phrase, next_phrase.phrase) > 0.9:
                phrase.add_similar(next_phrase)

def main():
    # Find something better!
    if init_fail:
        return

    dictionary = interface.read_dictionary()
    if dictionary is None:
        return 
    
    # keyspaces = interface.read_keyspaces()
    keyspaces = ['new_btpucp']

    # feature_list = interface.read_features()
    feature_list = ['Description']

    #ngrams = interface.read_ngrams()
    ngrams = (1,3)

    #dfs = interface.read_dfs()
    dfs = (0.1,0.9)

    documents = get_documents(keyspaces, feature_list)

    phrases = get_phrases(documents, ngrams, dfs, dictionary)

    model = get_word2vec()

    similars = get_similars(phrases, model)
    #print_similars()


if __name__ == "__main__":
    main()
    print("Adios!")
