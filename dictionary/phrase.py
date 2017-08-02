from dictionary import SYMPLICITY_KEYSPACE


class Phrase:
    def __init__(self, name, quantity, source, state=None):
        self.name = name
        self.quantity = quantity
        self.source = source
        self.state = state

    @staticmethod
    def _cmp(a, b):
        if a < b:
            return -1
        elif a > b:
            return 1
        else: return 0

    def __cmp__(self, cmp_phrase):
        if self.source == SYMPLICITY_KEYSPACE:
            if cmp_phrase.source != SYMPLICITY_KEYSPACE:
                return 1
            else:
                return self._cmp(self.quantity, cmp_phrase.quantity)
        else:
            if cmp_phrase.source == SYMPLICITY_KEYSPACE:
                return -1
            else:
                return self._cmp(self.quantity, cmp_phrase.quantity)

    def __lt__(self, cmp_phrase):
        return self.__cmp__(cmp_phrase) < 0

    def __str__(self):
        return str(self.name) + " " + str(self.quantity)

    def set_state(self, state):
        self.state = state

    def add_quantity(self, quantity):
        self.quantity += quantity


class Representative:
    def __init__(self, state, name, source, phrases=[]):
        self.state = state
        self.name = name
        self.phrases = phrases
        self.source = source

    def add_phrase(self, name, quantity, source):
        phrase = Phrase(name, quantity, source)
        print(phrase.name)
        self.phrases.append(phrase)

    @classmethod
    def ExportAsCsv(cls, representatives, filename):

        f = open(filename, 'w')

        print("Representante, Frase, Aceptar?", file=f)
        for rep in representatives:
            for phrase in rep.phrases:
                if rep.state is None:
                    state = ""
                    print(", ".join([rep.name, phrase.name, state]), file=f)
