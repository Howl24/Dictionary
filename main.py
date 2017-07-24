from dictionary import Interface
from dictionary import Dictionary
from dictionary import Offer
from dictionary import Document
from dictionary import Phrase
from dictionary import YES_RESPONSES
from dictionary import CREATE_BOW
from dictionary import SAVE_BOW
from dictionary import CLOSE
from sklearn.feature_extraction.text import CountVectorizer
from dictionary import stop_spanish
from dictionary import interface
import gensim

import sys


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

            documents.append(Document(text, keyspace))

    return documents


def get_phrases(documents, ngrams, dfs, dictionary):
    stopwords = dictionary.all_phrases() + stop_spanish
    min_ngrams = ngrams[0]
    max_ngrams = ngrams[1]

    min_df = dfs[0]
    max_df = dfs[1]

    cnt_vectorizer = CountVectorizer(stop_words=stopwords,
                                     ngram_range=(min_ngrams, max_ngrams),
                                     max_df=max_df, min_df=min_df,
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
                # Initialize a 2 lenght list [cnt, source]
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


def remove(list1, list2):
    new_list = [x for x in list1 if x not in list2]
    return new_list


def group_phrases(phrases, model):
    phrases.sort()

    grouped_phrases = []
    while(len(phrases) != 0):
        current_phrase = phrases[0]

        removed = []
        removed.append(current_phrase)
        grouped_phrases.append(current_phrase)

        for comp_phrase in phrases:
            if current_phrase != comp_phrase and \
               model.wv.similarity(current_phrase.phrase,
                                   comp_phrase.phrase) > 0.9:
                current_phrase.add_similar(comp_phrase.phrase)

                removed.append(comp_phrase)

        phrases = remove(phrases, removed)

    return grouped_phrases


def print_similars(group_phrases, dictionary):
    filename = dictionary.name + "_frases.csv"
    f = open(filename, 'w')

    print(len(group_phrases))
    for phrase in group_phrases:
        f.write(phrase.phrase + "\n")
        for similar in phrase.similars:
            f.write(phrase.phrase + ", " + similar + "\n")


def ask_load_data():
    msg = "Desea cargar un archivo de resultados?"
    response = interface.read_boolean(msg)
    return response


def load_file(dictionary):
    filename = dictionary.name + "_frases.csv"
    file = open(filename, 'r')

    phrases = {}
    for line in file:
        terms = line.split(',')
        if len(terms) == 3:
            phrase = terms[0]
            similar = terms[1]
            response = terms[2].strip()

            if response in YES_RESPONSES:
                response = True
            else:
                print("foo"+str(response)+"foo")
                response = False

            if phrase not in phrases:
                new_phrase = Phrase(response, phrase, [similar], 0,
                                    "new_btpucp")
                phrases[phrase] = new_phrase
            else:
                phrases[phrase].add_similar(similar)

    for phrase in phrases:
        dictionary.insert_phrase(phrases[phrase])


def create_bow(interface):
    dic = interface.read_dictionary()
    if not dic:
        return

    if not dic.sources:
        interface.read_configuration(dic)


def save_bow(interface):
    pass


def main():
    file = open('foo.err', 'w')
    sys.stdout = file
    sys.stderr = file

    Dictionary.PrepareStatements()
    interface = Interface()

    mode = None
    while (mode != CLOSE):
        mode = interface.choose_mode()
        if mode == CREATE_BOW:
            create_bow(interface)

        if mode == SAVE_BOW:
            save_bow(interface)

    return

    # response = ask_load_data()
    # if response is True:
    #     load_file(dictionary)
    #     return
    #
    # # keyspaces = interface.read_keyspaces()
    # keyspaces = ['new_btpucp']

    # # feature_list = interface.read_features()
    # feature_list = ['Description']

    # #ngrams = interface.read_ngrams()
    # ngrams = (1,3)

    # #dfs = interface.read_dfs()
    # dfs = (0.1,0.9)

    # documents = get_documents(keyspaces, feature_list)

    # phrases = get_phrases(documents, ngrams, dfs, dictionary)

    # model = get_word2vec()

    # phrases_with_similars = group_phrases(phrases, model)
    # print_similars(phrases_with_similars, dictionary)


if __name__ == "__main__":
    main()
