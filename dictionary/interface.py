from dictionary import Dictionary
from dictionary import Offer
import curses
from pick import pick
from dictionary import YES
from dictionary import NO
from dictionary import MODE_CHOICES
from dictionary import KEYSPACES


class Interface:
    def __init__(self):
        self.stdscr = curses.initscr()

    def __del__(self):
        self.stdscr.addstr(1, 1, "Pulse cualquier tecla para terminar.")
        self.stdscr.getkey()
        curses.endwin()

    def read_string(self, msg):
        self.stdscr.addstr(1, 1, msg)
        response = self.stdscr.getstr().decode("utf-8")
        self.stdscr.clear()
        return response

    def read_boolean(self, msg):
        options = [YES, NO]
        option, index = pick(options, msg, indicator="=>")
        self.stdscr.clear()
        return option == YES

    def read_int(self, msg, row, col, error_value=None):
        self.stdscr.addstr(row, col, msg)
        self.stdscr.clrtoeol()
        try:
            return int(self.stdscr.getstr().decode("utf-8"))
        except ValueError:
            return error_value

    def read_double(self, msg, row, col, error_value=None):
        self.stdscr.addstr(row, col, msg)
        self.stdscr.clrtoeol()
        try:
            return float(self.stdscr.getstr().decode("utf-8"))
        except ValueError:
            return error_value

    def read_dictionary(self):
        msg = "Ingrese el nombre del diccionario: "
        dictionary_name = self.read_string(msg)
        dictionary = Dictionary.Select(dictionary_name)
        if dictionary is None:
            msg = "El diccionario ingresado no existe.\n" + \
                  "Desea crear uno nuevo?"
            response = self.read_boolean(msg)
            if response is True:
                dictionary = Dictionary.New(dictionary_name)

        return dictionary

    def read_configuration(self, dictionary):
        sources = self.read_keyspaces()
        # Only for develop...
        #features = self.read_features(sources)
        features = {"new_btpucp": {"Description", "Qualifications"}}

        ngrams = self.read_ngrams()
        dfs = self.read_dfs()
        last_bow = (0,0)

        for source in sources:
            dictionary.add_configuration(source,
                                         features[source],
                                         ngrams,
                                         dfs,
                                         last_bow)
        return dictionary

    def read_dfs(self):
        self.stdscr.addstr(1, 1,
                           "Ingrese el rango de frecuencias a obtener")

        msg = "Mínimo: "
        min_df = None
        while (min_df is None):
            min_df = self.read_double(msg, 3, 1)

        msg = "Máximo: "
        max_df = None
        while(max_df is None):
            max_df = self.read_double(msg, 5, 1)

        self.stdscr.clear()
        return (min_df, max_df)

    def read_ngrams(self):
        self.stdscr.addstr(1, 1,
                           "Ingrese el numero minimo y maximo de n-gramas")

        msg = "Mínimo: "
        min_ngram = None
        while (min_ngram is None):
            min_ngram = self.read_int(msg, 3, 1)

        msg = "Máximo: "
        max_ngram = None
        while(max_ngram is None):
            max_ngram = self.read_int(msg, 5, 1)

        self.stdscr.clear()
        return (min_ngram, max_ngram)

    def read_keyspaces(self):
        msg = "Seleccione los keyspaces a partir de los cuales\n" + \
              "desea construir el bow."

        selected = pick(KEYSPACES, msg,
                        multi_select=True,
                        min_selection_count=1,
                        indicator="=>")
        self.stdscr.clear()

        return [option for (option, index) in selected]

    def load_features(self, sources):
        # Slow
        features = {}
        for source in sources:
            features[source] = set()
            offers = Offer.SelectAll(source)
            for offer in offers:
                for feature in offer.features:
                    features[source].add(feature)

        return features

    def read_features(self, sources):
        self.stdscr.addstr(1, 1, "Espere un momento...")
        self.stdscr.refresh()
        all_features = self.load_features(sources)

        selected_features = {}
        for source, features in all_features.items():
            msg = "Seleccione los features del keyspace: {0}".format(source)
            options = list(features)
            selected = pick(options,
                            msg,
                            multi_select=True,
                            min_selection_count=1,
                            indicator="=>")

            selected_features[source] = set()
            for option, index in selected:
                selected_features[source].add(option)

            self.stdscr.clear()
        return selected_features

    def choose_mode(self):
        msg = "Escoja una acción a realizar: "
        option, index = pick(MODE_CHOICES, msg, indicator="=>")
        self.stdscr.clear()
        return option


    def save_configuration(self, dictionary):
        msg = "Desea guardar la configuración: "
        response = self.read_boolean(msg)
        if response is True:
            dictionary.save_configuration()

        return response

    def get_new_bow(self, dictionary):
        self.stdscr.addstr(1, 1, "Espere un momento...")
        self.stdscr.refresh()
        new_bow = dictionary.get_new_bow()
        self.stdscr.clear()
        self.stdscr.addstr(1, 1, "El bow ha sido exportado")
        self.stdscr.refresh()
        self.stdscr.getkey()
        return new_bow

# def read_string(message=""):
#    response = input(message)
#    return response
#
#
# def read_boolean(message):
#    boolean_message = message + " (S/N)"
#    response = input(boolean_message)
#    return response in dictionary.YES_RESPONSES
#
#
# def read_int(message, error_value=None):
#    response = input(message)
#    try:
#        return int(response)
#    except ValueError:
#        return error_value
#
#
# def read_double(message, error_value=None):
#    response = input(message)
#    try:
#        return float(response)
#    except ValueError:
#        return error_value
#
#
# def read_dictionary():
#    dictionary_name = read_string("Ingrese el nombre del diccionario: ")
#    dictionary = Dictionary.Select(dictionary_name)
#    if dictionary is None:
#        print("El diccionario ingresado no existe")
#        response = read_boolean("Desea crear un diccionario nuevo?")
#        if response is True:
#            dictionary = Dictionary.New(dictionary_name)
#
#    print()
#    return dictionary
#
#
# def read_list(msg):
#    print(msg)
#    responses = []
#    keep_reading = True
#    while(keep_reading):
#        response = read_string()
#        if not response:
#            keep_reading = False
#        else:
#            responses.append(response)
#
#    return responses
#
#
# def read_keyspaces():
#    msg = "Indique los keyspaces a partir " + \
#          "de los cuales desea construir el diccionario"
#
#    return read_list(msg)
#
#
# def read_features():
#    msg = "Indique los features a partir " + \
#          "de los cuales se desea obtener el diccionario"
#
#    return read_list(msg)
#
#
# def read_ngrams():
#    msg = "Indique el numero mínimo y máximo de n-gramas a obtener"
#    print(msg)
#
#    msg = "Mínimo: "
#    min_ngram = read_int(msg)
#
#    msg = "Máximo: "
#    max_ngram = read_int(msg)
#
#    return min_ngram, max_ngram
#
# def read_dfs():
#    msg = "Indique los limites mínimo y máximo de frecuencias por palabra"
#    print(msg)
#
#    msg = "DF Mínimo: "
#    min_df = read_double(msg)
#
#    msg = "DF Máximo: "
#    max_df = read_double(msg)
#
#    return min_df, max_df
