from dictionary import SYMPLICITY_KEYSPACE

class Phrase:

    def __init__(self, state, phrase, similars, frec, source):
        self.state = state
        self.phrase = phrase
        self.similars = similars
        self.frec = frec
        self.source = source


    @staticmethod
    def _cmp(a, b):
        return (a > b) - (a < b)


    def __cmp__(self, other):
        if self.source == SYMPLICITY_KEYSPACE:
            if other.source != SYMPLICITY_KEYSPACE:
                return 1
            else:
                return self._cmp(self.frec, other.frec)
        else:
            if other.source == SYMPLICITY_KEYSPACE:
                return -1
            else:
                return self._cmp(self.frec, other.frec)

    def __lt__(self, other):
        return self.__cmp__(other) < 0


    @classmethod
    def ByCassandraRows(cls, rows):
        phrases = []
        for row in rows:
            phrase = cls(row.state, row.phrase, row.similars,0, "new_btpucp")
            phrases.append(phrase)

        return phrases

    def add_similar(self, phrase):
        self.similars.append(phrase)

    def print(self):
        print("- Phrase " + self.phrase)
        for similar in self.similars:
            print("  " + similar)
