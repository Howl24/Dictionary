import dictionary
from dictionary import Dictionary


def read_string(message=""):
    response = input(message)
    return response


def read_boolean(message):
    boolean_message = message + " (S/N)"
    response = input(boolean_message)
    return response in dictionary.YES_RESPONSES


def read_int(message, error_value=None):
    response = input(message)
    try:
        return int(response)
    except ValueError:
        return error_value


def read_dictionary():
    dictionary_name = read_string("Ingrese el nombre del diccionario: ")
    dictionary = Dictionary.Select(dictionary_name)
    if dictionary is None:
        print("El diccionario ingresado no existe")
        response = read_boolean("Desea crear un diccionario nuevo?")
        if response is True:
            dictionary = Dictionary.New(dictionary_name)

    print()
    return dictionary


def read_list(msg):
    print(msg)
    responses = []
    keep_reading = True
    while(keep_reading):
        response = read_string()
        if not response:
            keep_reading = False
        else:
            responses.append(response)


def read_keyspaces():
    msg = "Indique los keyspaces a partir " + \
          "de los cuales desea construir el diccionario"

    return read_list(msg)


def read_features():
    msg = "Indique los features a partir " + \
          "de los cuales se desea obtener el diccionario"

    return read_list(msg)


def read_ngrams():
    msg = "Indique el numero mínimo y máximo de n-gramas a obtener"
    print(msg)

    msg = "Mínimo: "
    min_ngram = read_int(msg)

    msg = "Máximo: "
    max_ngram = read_int(msg)

    return min_ngram, max_ngram
