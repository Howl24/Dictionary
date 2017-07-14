import dictionary
from dictionary import Dictionary


def read_string(message):
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

    return dictionary
