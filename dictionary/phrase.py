class Phrase:

    def __init__(self, state, phrase, similars):
        self.state = state
        self.phrase = phrase
        self.similars = similars

    @classmethod
    def ByCassandraRows(cls, rows):
        phrases = []
        for row in rows:
            phrase = Phrase(row.state, row.phrase, row.similars)
            phrases.append(phrase)

        return phrases

    def print(self):
        print("- Phrase " + self.phrase)
        for similar in self.similars:
            print("  " + similar)
