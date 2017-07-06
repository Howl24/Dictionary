from dictionary import get_dictionary
from dictionary import new_dictionary
from constants import yes_responses

def read_string(message):
    response = input(message)
    return response

def read_boolean(message):
    boolean_message = message + " (S/N)"
    response = input(boolean_message)

    return response in yes_responses

def read_dictionary():
    dictionary_name = read_string("Ingrese el nombre del diccionario: ")
    dictionary = get_dictionary(dictionary_name)

    if dictionary.not_exists:
        print("El diccionario ingresado no existe.")
        create_dictionary = read_boolean("Desea crear un nuevo diccionario?")
        if create_dictionary:
            dictionary = new_dictionary(dictionary_name)

    return dictionary

def main():
    dictionary = read_dictionary()
    if dictionary.not_exists:
        return

    keyspaces = read_keyspaces()
    feature_list = read_feature_list()
    ngrams = read_ngrams()
    documents = get_documents(keyspaces, feature_list)
    phrases = get_phrases(documents, dictionary)
    word2vec = get_word2vec()

    similars = get_similars(phrases, word2vec)
    print_similars()


if __name__ == "__main__":
    main()
    print("Adios!")
