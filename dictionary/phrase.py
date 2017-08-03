from dictionary import SYMPLICITY_KEYSPACE


class Phrase:
    def __init__(self, name, quantity, source, state):
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
        else:
            return 0

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
    def __init__(self, name, state, phrases=[]):
        self.name = name
        self.state = state
        self.phrases = phrases

    def add_phrase(self, name, quantity, source, state):
        phrase = Phrase(name, quantity, source, state)
        self.phrases.append(phrase)


    def __str__(self):
        lines = []
        lines.append("Representative: " + self.name)
        for phrase in self.phrases:
            lines.append(str(phrase))

        return "\n".join(lines)

    @classmethod
    def ExportAsCsv(cls, representatives, filename_representatives, filename_review):

        # Representatives and similar phrases
        f_representatives = open(filename_representatives, 'w')
        print("Representante, Frase Similar", file=f_representatives)
        for rep in representatives:
            for phrase in rep.phrases:
                if rep.state is None:
                    state = ""
                    print(", ".join([rep.name, phrase.name]), file=f_representatives)

        # Only representatives to review
        f_review = open(filename_review, 'w')
        print("Representante, Aceptar?", file=f_review)
        for rep in representatives:
            if rep.state is None:
                state = ""
                print(", ".join([rep.name, state]), file=f_review)

    def set_state(self, state):
        self.state = state
