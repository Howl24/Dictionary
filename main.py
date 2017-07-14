from dictionary import read_dictionary

def main():
    dictionary = read_dictionary()
    if dictionary is None:
        return 

    dictionary.print()
    #keyspaces = read_keyspaces()
    #feature_list = read_feature_list()
    #ngrams = read_ngrams()
    #documents = get_documents(keyspaces, feature_list)
    #phrases = get_phrases(documents, dictionary)
    #word2vec = get_word2vec()

    #similars = get_similars(phrases, word2vec)
    #print_similars()


if __name__ == "__main__":
    main()
    print("Adios!")
