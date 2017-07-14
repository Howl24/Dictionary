from dictionary import interface
from dictionary import init_fail

def main():
    # Find something better!
    if init_fail:
        return

    dictionary = interface.read_dictionary()
    if dictionary is None:
        return 

    keyspaces = interface.read_keyspaces()
    feature_list = interface.read_features()
    ngrams = interface.read_ngrams()
    #documents = get_documents(keyspaces, feature_list)
    #phrases = get_phrases(documents, dictionary)
    #word2vec = get_word2vec()

    #similars = get_similars(phrases, word2vec)
    #print_similars()


if __name__ == "__main__":
    main()
    print("Adios!")
