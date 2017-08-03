from dictionary import Dictionary
from dictionary import Offer
import curses
from pick import pick
from dictionary import YES
from dictionary import NO
from dictionary import MODE_CHOICES
from dictionary import KEYSPACES
import os


class Interface:
    # TODO
    # Update configuration interface
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

    def read_dictionary(self, new=True):
        # TODO
        # Move New dictionary question out of this method.
        msg = "Ingrese el nombre del diccionario: "
        dictionary_name = self.read_string(msg)
        dictionary = Dictionary.ByName(dictionary_name)
        if dictionary is None:
            if new is True:
                msg = "El diccionario ingresado no existe.\n" + \
                      "Desea crear uno nuevo?"
                response = self.read_boolean(msg)
                if response is True:
                    dictionary = Dictionary.New(dictionary_name)
            else:
                self.stdscr.addstr(1, 1, "El diccionario ingresado no existe")
                self.stdscr.getkey()

        return dictionary

    def read_configuration(self, dictionary):
        sources = self.read_keyspaces()
        features = self.read_features(sources)

        ngrams = self.read_ngrams()
        dfs = self.read_dfs()
        last_bow = (0, 0)

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
        self.stdscr.addstr(1, 1, "Se estan revisando los features existentes")
        self.stdscr.addstr(1, 1, "Espere un momento...")
        self.stdscr.refresh()
        all_features = self.load_features(sources)

        selected_features = {}
        for source, features in all_features.items():

            msg = "Seleccione los features del keyspace: {0}".format(source)
            options = sorted(list(features))
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

    def export_new_bow(self, dictionary):
        self.stdscr.addstr(1, 1, "El bow esta siendo procesado")
        self.stdscr.addstr(2, 1, "Espere un momento...")
        self.stdscr.refresh()
        dictionary.export_new_bow()
        self.stdscr.clear()
        self.stdscr.addstr(1, 1, "El bow ha sido exportado")
        self.stdscr.addstr(2, 1, "                         ")
        self.stdscr.refresh()
        self.stdscr.getkey()
        self.stdscr.clear()

    def choose_filename(self, msg, extension):
        filenames = [filename for filename in os.listdir() if extension in filename]
        option, index = pick(filenames, msg, indicator="=>")
        self.stdscr.clear()
        return option

    def import_bow(self, dictionary):
        msg = "Seleccione el archivo con el bow que desea ingresar"
        extension = ".csv"
        filename = self.choose_filename(msg, extension)

        # wait?
        dictionary.import_bow(filename)
        self.stdscr.addstr(1, 1, "El bow ha sido ingresado al diccionario")
        self.stdscr.getkey()

    def import_review(self, dictionary):
        msg = "Seleccione el archivo con la revisión que desea ingresar"
        extension = ".csv"
        filename = self.choose_filename(msg, extension)

        # wait?
        dictionary.import_representative_review(filename)
        self.stdscr.addstr(1, 1, "La revision ha sido ingresada al diccionario")
        self.stdscr.getkey()
