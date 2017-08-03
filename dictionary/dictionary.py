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


class Dictionary:
    session = None
    keyspace = "general"
    phrase_table_name = "new_dictionary"
    conf_table_name = "dictionary_configuration"
    tmp_table_name = "temp_dictionary"
    insert_stmt = None
    select_stmt = None
    delete_stmt = None
    insert_conf_stmt = None
    select_conf_stmt = None
    select_representative_stmt = None
    insert_tmp_stmt = None
    select_tmp_stmt = None
    select_all_tmp_stmt = None

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
                     (name, representative, phrase, quantity, source, state)
                     VALUES
                     (?, ?, ?, ?, ?, ?);
                     """.format(cls.phrase_table_name)

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     name = ?;
                     """.format(cls.phrase_table_name)

        cmd_select_representative = """
                                    SELECT * FROM {0} WHERE
                                    name = ? AND
                                    representative = ?;
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

        cmd_insert_tmp = """
                         INSERT INTO {0}
                         (name, phrase, quantity, source, representative, state)
                         VALUES
                         (?, ?, ?, ?, ?, ?);
                         """.format(cls.tmp_table_name)

        cmd_select_tmp = """
                         SELECT * FROM {0} WHERE
                         name = ? AND
                         phrase = ?;
                         """.format(cls.tmp_table_name)

        cmd_select_all_tmp = """
                             SELECT * FROM {0} WHERE
                             name = ?;
                             """.format(cls.tmp_table_name)

        cls.insert_stmt = cls.session.prepare(cmd_insert)
        cls.select_stmt = cls.session.prepare(cmd_select)
        cls.select_representative_stmt = cls.session.prepare(cmd_select_representative)

        cls.insert_conf_stmt = cls.session.prepare(cmd_insert_conf)
        cls.select_conf_stmt = cls.session.prepare(cmd_select_conf)

        cls.insert_tmp_stmt = cls.session.prepare(cmd_insert_tmp)
        cls.select_tmp_stmt = cls.session.prepare(cmd_select_tmp)
        cls.select_all_tmp_stmt = cls.session.prepare(cmd_select_all_tmp)

        try:
            pass
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
               representative text,
               phrase set<text>,
               quantity int,
               source text,
               state boolean,
               PRIMARY KEY (name, representative));
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

        cmd_create_tmp_table = """
                CREATE TABLE IF NOT EXISTS {0} (
                name            text,
                phrase          text,
                quantity        int,
                source          text,
                state           boolean,
                representative  text,
                PRIMARY KEY (name, phrase));
                """.format(cls.tmp_table_name)

        cls.session.execute(cmd_create_phrase_table)
        cls.session.execute(cmd_create_configuration_table)
        cls.session.execute(cmd_create_tmp_table)

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

    def get_bow_filenames(self):
        filename_representatives = self.name + "_similares_" + ".csv"
        filename_review = self.name + "_a_revisar.csv"

        return filename_representatives, filename_review

    def export_new_bow(self):
        # Hashed by source to improve quantity update
        old_phrases = self.get_old_phrases_by_source()

        all_phrases = []
        for source in self.sources:
            documents = []
            offers = Offer.SelectSince(source, self.last_bow)
            # print(len(offers))
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

        filenames = self.get_bow_filenames()
        Representative.ExportAsCsv(representatives, filenames[0], filenames[1])

        self.save_tmp_representatives(representatives)

    def save_tmp_representatives(self, representatives):
        for rep in representatives:
            for phrase in rep.phrases:
                dict_name = self.name
                self.session.execute(self.insert_tmp_stmt,
                                     (dict_name,
                                      phrase.name, phrase.quantity, phrase.source,
                                      rep.name, rep.state,))

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
                    # print(comp_phrase.name)
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

    def import_bow(self, filename):
        f = open(filename, 'r')
        dict_name = self.name

        wrong_lines = []
        for idx, line in enumerate(f):
            if idx == 0:
                continue
            data = line.split(',')

            try:
                rep_name = data[0].strip()
                phrase_name = data[1].strip()
            except:
                wrong_lines.append(idx)
                continue

            result = self.session.execute(self.select_tmp_stmt, (dict_name, phrase_name,))
            try:
                row = result[0]
            except:
                wrong_lines.append(idx)
                continue

            self.session.execute(self.insert_tmp_stmt,
                                 (dict_name,
                                  row.phrase, row.quantity, row.source,
                                  rep_name,))

        for line in wrong_lines:
            print(line)

    def select_representative(self, rep_name):
        rows = self.session.execute(self.select_representative_stmt,
                                    (self.name, rep_name,))

        representative = Representative(state=None, name=rep_name, source=None, phrases=[])

        if rows:
            for row in rows:
                phrase = row.phrase
                quantity = row.quantity

                state = row.state
                if state:
                    representative.state = state

                source = row.source
                if source:
                    representative.source = source

                representative.add_phrase(phrase, quantity, source)

        return representative

    def insert(self, representative):

        dict_name = self.name
        rep_name = representative.name
        state = representative.state

        for phrase in representative.phrases:
            phrase_name = phrase.name
            quantity = phrase.quantity
            source = phrase.source

        self.session.execute(self.cmd_insert_stmt,
                             (dict_name, source, rep_name,
                              phrase_name, quantity, state,))

    def import_representative_review(self, filename):
        f = open(filename, 'r')
        dict_name = self.name

        rows = self.session.execute(self.select_all_tmp_stmt,
                                    (dict_name,))

        representatives = {}
        if rows:
            for row in rows:
                rep_name = row.representative
                state = row.state
                if rep_name is None:
                    rep_name = ""

                if rep_name not in representatives:
                    representatives[rep_name] = Representative(state, rep_name, row.source, [])

                representatives[rep_name].add_phrase(row.phrase, row.quantity, row.source)

        wrong_lines = []
        for idx, line in enumerate(f):
            if idx == 0:
                continue
            data = line.split(',')

            try:
                rep_name = data[0].strip()
                state = data[1].strip()
            except:
                wrong_lines.append(idx)
                continue

            if state in dictionary.ACCEPT_REPRESENTATIVE_RESPONSES:
                state = True
            elif state in dictionary.REJECT_REPRESENTATIVE_RESPONSES:
                state = False
            else:
                wrong_lines.append(idx)
                continue

            representatives[rep_name].set_state(state)

        self.save_tmp_representatives(representatives.values())
