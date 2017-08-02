from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
from dictionary import Offer
from dictionary import Representative
from dictionary import Phrase
from dictionary import stop_spanish
from dictionary import process_text
from sklearn.feature_extraction.text import CountVectorizer
import dictionary
import gensim
import time


class Dictionary:
    session = None
    keyspace = "general"
    phrase_table_name = "new_dictionary"
    conf_table_name = "dictionary_configuration"
    insert_stmt = None
    select_stmt = None
    delete_stmt = None
    insert_conf_stmt = None
    select_conf_stmt = None

    def __init__(self, name, accepted, rejected, sources=[],
                 features={}, ngrams=None, dfs=None, last_bow=0):
        self.name = name
        self.accepted = accepted
        self.rejected = rejected
        self.sources = sources
        self.features = features
        self.ngrams = ngrams
        self.dfs = dfs
        self.last_bow = last_bow

    # Pre  :
    #   - Cluster instance
    # Post :
    #   - Class session instantiated
    @classmethod
    def ConnectToDatabase(cls, cluster):
        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable:
            raise

    # Pre:
    #   - Class session instance
    # Post:
    #   - Class PreparedStatements instantiated
    @classmethod
    def PrepareStatements(cls):
        cmd_insert = """
                     INSERT INTO {0}
                     (state, name, phrase, similars)
                     VALUES
                     (?, ?, ?, ?);
                     """.format(cls.phrase_table_name)

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     name = ?;
                     """.format(cls.phrase_table_name)

        cmd_insert_conf = """
                          INSERT INTO {0}
                          (name, source, features, ngrams, dfs, last_bow)
                          VALUES
                          (?, ?, ?, ?, ?, ?);
                          """.format(cls.conf_table_name)

        cmd_select_conf = """
                          SELECT * FROM {0} WHERE
                          name = ?;
                          """.format(cls.conf_table_name)

        cmd_delete = """
                     DELETE FROM {0} WHERE
                     state = ? AND
                     name = ?;
                     """.format(cls.phrase_table_name)

        try:
            #cls.insert_stmt = cls.session.prepare(cmd_insert)
            cls.select_stmt = cls.session.prepare(cmd_select)
            #cls.delete_stmt = cls.session.prepare(cmd_delete)

            cls.insert_conf_stmt = cls.session.prepare(cmd_insert_conf)
            cls.select_conf_stmt = cls.session.prepare(cmd_select_conf)
        except InvalidRequest:
            print("Tabla no configurada.")
            print("Utilice la funcion CreateTable para crear una tabla")
            print()
            return dictionary.UNSUCCESSFUL_OPERATION

        return dictionary.SUCCESSFUL_OPERATION

    # Pre:
    #   - Class session instancej
    # Post:
    #   - Dictionary DB_Table created
    @classmethod
    def CreateTables(cls):
        cmd_create_phrase_table = """
               CREATE TABLE IF NOT EXISTS {0} (
               name text,
               source text,
               representative text,
               phrases set<text>,
               quantity int,
               state boolean,
               PRIMARY KEY (name, source, representative));
               """.format(cls.phrase_table_name)

        cmd_create_configuration_table = """
               CREATE TABLE IF NOT EXISTS {0} (
               name         text,
               source       text,
               features     set<text>,
               ngrams       tuple<int, int>,
               dfs          tuple<double, double>,
               last_bow     tuple<int, int>,
               PRIMARY KEY (name, source));
               """.format(cls.conf_table_name)

        cls.session.execute(cmd_create_phrase_table)
        cls.session.execute(cmd_create_configuration_table)

        print("Las tablas de diccionarios se crearon correctamente")
        return dictionary.SUCCESSFUL_OPERATION

    @classmethod
    def Select(cls, dictionary_name):
        """Return a dictionary from database"""

        configuration = cls.session.execute(cls.select_conf_stmt,
                                            (dictionary_name,))

        rows = cls.session.execute(cls.select_stmt,
                                   (dictionary_name,))

        if not configuration:
            return None
        else:
            if not rows:
                rows = []

            return Dictionary.FromCassandra(dictionary_name,
                                            configuration,
                                            rows)

    @classmethod
    def New(cls, dictionary_name):
        name = dictionary_name
        accepted_phrases = []
        rejected_phrases = []
        return cls(name, accepted_phrases, rejected_phrases)

    @classmethod
    def FromCassandra(cls, dictionary_name, configuration, phrases):

        dictionary = Dictionary.New(dictionary_name)

        # Add dictionary configuration
        for result in configuration:
            source = result.source
            features = result.features
            ngrams = result.ngrams
            dfs = result.dfs
            last_bow = result.last_bow
            dictionary.add_configuration(source, features, ngrams, dfs, last_bow)

        # Add dictionary phrases
        for result in phrases:
            source = result.source
            representative = result.representative
            phrase = result.phrase
            quantity = result.quantity
            state = result.state
            dictionary.add_phrase(source, representative, phrase, quantity, state)

        return dictionary

    def add_configuration(self, source, features, ngrams, dfs, last_bow):
        """Add source to container and map features"""
        self.sources.append(source)
        self.features[source] = features
        self.ngrams = ngrams
        self.dfs = dfs
        self.last_bow = last_bow

    def add_phrase(self, source, representative, phrase, quantity, state):
        if state is True:
            if representative not in self.accepted:
                self.accepted[representative] = Representative(state, representative, source)

            self.accepted[representative].add_phrase(phrase, quantity, source)

        else:
            if representative not in self.rejected:
                self.rejected[representative] = Representative(state, representative, source)

            self.rejected[representative].add_phrase(phrase, quantity, source)

    def print(self):
        print("Dictionary Name: " + self.name)
        for phrase in self.accepted_phrases:
            phrase.print()

    def insert_phrase(self, phrase):
        self.session.execute(self.insert_stmt,
                             (phrase.state, self.name,
                              phrase.phrase, phrase.similars))

    def save_configuration(self):
        for source in self.sources:
            self.session.execute(self.insert_conf_stmt,
                                 (self.name,
                                  source,
                                  self.features[source],
                                  self.ngrams,
                                  self.dfs,
                                  self.last_bow))

    def get_bow_filename(self):
        old_month = str(self.last_bow[0])
        old_year = str(self.last_bow[1])

        new_month = time.strftime("%m")
        new_year = time.strftime("%Y")

        filename = self.name + "_desde_" + old_month + "-" + old_year + \
                    "__hasta__" + new_month + "-" + new_year + \
                    "_bow.csv"

        return filename

    def export_new_bow(self):
        # Hashed by source to improve quantity update
        old_phrases = self.get_old_phrases_by_source()

        all_phrases = []
        for source in self.sources:
            documents = []
            offers = Offer.SelectSince(source, self.last_bow)
            print(len(offers))
            features = self.features[source]

            for offer in offers:
                text = ""
                for feature in features:
                    if feature in offer.features:
                        text += offer.features[feature] + ' '
                documents.append(text)

            phrases = self.get_phrases(documents, source, old_phrases[source])
            all_phrases += phrases

        model = self.get_word2vec()
        representatives = self.get_representatives(all_phrases, model)

        filename = self.get_bow_filename()
        Representative.ExportAsCsv(representatives, filename)


    @staticmethod
    def remove(list1, list2):
        new_list = [x for x in list1 if x not in list2]
        return new_list

    def get_representatives(self, phrases, model):
        phrases.sort(reverse=True)

        representatives = []
        # print("Grouping ...")
        while (len(phrases) != 0):
            current_phrase = phrases[0]

            removed = []

            rep_name = current_phrase.name
            source = current_phrase.source
            state = None

            representative = Representative(state, rep_name, source, [])

            # print()
            # print("Representative: " + representative.name)
            # print("Size: " + str(len(representative.phrases)))

            for comp_phrase in phrases:
                ws1 = representative.name.split()
                ws2 = comp_phrase.name.split()

                if model.wv.n_similarity(ws1, ws2) > dictionary.SIMILARITY_PERCENTAGE:
                    representative.add_phrase(comp_phrase.name, comp_phrase.quantity, comp_phrase.source)
                    print(comp_phrase.name)
                    removed.append(comp_phrase)

            phrases = self.remove(phrases, removed)
            # print("End Size: " + str(len(representative.phrases)))
            representatives.append(representative)

        # print("\n")
        # print("Printing...")

        return representatives

    def get_word2vec(self):
        model = gensim.models.Word2Vec.load('w2v/model')
        return model

    def get_phrases(self, documents, source, old_phrases):
        min_ngrams = self.ngrams[0]
        max_ngrams = self.ngrams[1]

        min_df = self.dfs[0]
        max_df = self.dfs[1]

        cnt_vectorizer = CountVectorizer(stop_words=stop_spanish,
                                         ngram_range=(min_ngrams, max_ngrams),
                                         max_df=max_df, min_df=min_df,
                                         )

        processed_documents = []
        for doc in documents:
            processed_doc = process_text(doc)
            processed_documents.append(processed_doc)

        
        terms_matrix = cnt_vectorizer.fit_transform(processed_documents)
        phrase_names = cnt_vectorizer.get_feature_names()

        phrases = self.get_comparable_phrases(terms_matrix, phrase_names, source, old_phrases)

        return phrases

    def get_comparable_phrases(self, terms_matrix, phrase_names, source, old_phrases):
        # phrase_name as key
        phrases = {}

        # Add old phrases
        for phrase in old_phrases:
            name = phrase.name
            if name not in phrases:
                phrases[name] = phrase

        # Add new phrases
        for idx_doc, doc in enumerate(terms_matrix):
            for idx_phrase, name in enumerate(phrase_names):
                quantity = terms_matrix[idx_doc, idx_phrase]
                if name not in phrases:
                    phrases[name] = Phrase(name, quantity, source)

                phrases[name].add_quantity(quantity)

        return list(phrases.values())

    def get_old_phrases_by_source(self):
        phrases = {}
        for source in self.sources:
            phrases[source] = [] 

        for representative_name in self.accepted:
            representative = self.accepted[representative_name]
            for phrase in representative.phrases:
                phrases[phrase.source].append(phrase)

        for representative_name in self.rejected:
            representative = self.rejected[representative_name]
            for phrase in representative.phrases:
                phrases[phrase.source].append(phrase)

        return phrases

    def all_phrases(self):
        phrases = []
        for phrase in self.accepted_phrases:
            phrases.append(phrase.phrase)

        for phrase in self.rejected_phrases:
            phrases.append(phrase.phrase)

        return phrases
