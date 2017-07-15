from dictionary import interface
from dictionary import init_fail
from dictionary import Offer
from sklearn.feature_extraction.text import CountVectorizer


def get_documents(keyspaces, feature_list):
    documents = []
    for keyspace in keyspaces:
        # Find something better
        if not Offer.BuildPreparedStatements(keyspace):
            return None
        offers = Offer.SelectAll(keyspace)
        for offer in offers:
            document = ""
            for feature in feature_list:
                if feature in offer.features:
                    document += offer.features[feature] + ' '

            documents.append(document)
                
    return documents


def get_phrases(documents, ngrams, dfs, dictionary):
    stopwords = dictionary.all_phrases()
    min_ngrams = ngrams[0]
    max_ngrams = ngrams[1]

    min_df = dfs[0]
    max_df = dfs[1]

    cnt_vectorizer = CountVectorizer(stop_words = stopwords,
                                     ngram_range=(min_ngrams, max_ngrams),
                                     max_df = max_df, min_df = min_df,
                                     )

    cnt_vectorizer.fit(documents)
    feature_names = cnt_vectorizer.get_feature_names()
    print(feature_names)
    print(len(feature_names))


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
    if documents is None:
        return

    phrases = get_phrases(documents, ngrams, dfs, dictionary)
    #word2vec = get_word2vec()

    #similars = get_similars(phrases, word2vec)
    #print_similars()


if __name__ == "__main__":
    main()
    print("Adios!")
