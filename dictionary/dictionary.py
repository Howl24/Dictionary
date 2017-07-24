from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
from dictionary import Phrase
import dictionary


class Dictionary:
    session = None
    keyspace = "general"
    table_name = "new_dictionary"
    conf_table_name = "dictionary_configuration"
    insert_stmt = None
    select_stmt = None
    delete_stmt = None
    select_conf_stmt = None

    def __init__(self, name, accepted_phrases, rejected_phrases,
                 sources=[], features={}, ngrams=None, dfs=None):
        self.name = name
        self.accepted_phrases = accepted_phrases
        self.rejected_phrases = rejected_phrases
        self.sources = sources
        self.features = features
        self.ngrams = ngrams
        self.dfs = dfs

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
                     """.format(cls.table_name)

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     state = ? AND
                     name = ?;
                     """.format(cls.table_name)

        cmd_select_conf = """
                          SELECT * FROM {0} WHERE
                          name = ?;
                          """.format(cls.conf_table_name)

        cmd_delete = """
                     DELETE FROM {0} WHERE
                     state = ? AND
                     name = ?;
                     """.format(cls.table_name)

        try:
            cls.insert_stmt = cls.session.prepare(cmd_insert)
            cls.select_stmt = cls.session.prepare(cmd_select)
            cls.delete_stmt = cls.session.prepare(cmd_delete)
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
    def CreateTable(cls):
        cmd = """
               CREATE TABLE IF NOT EXISTS {0} (
               state boolean,
               name text,
               phrase text,
               similars set<text>,
               PRIMARY KEY ((state, name), phrase));
               """.format(cls.table_name)

        cmd = """
               CREATE TABLE IF NOT EXISTS {0} (
               name text,
               source text,
               features set<text>,
               PRIMARY KEY (name, source));
               """.format(cls.configuration_table_name)

        try:
            cls.session.execute(cmd)
        except:
            # print("No se pudo crear la tabla de diccionarios")
            # print(Exception.errors)
            return dictionary.UNSUCCESSFUL_OPERATION

        print("La tabla de diccionarios se creó correctamente")
        return dictionary.SUCCESSFUL_OPERATION

    @classmethod
    def Select(cls, dictionary_name):
        """Return a dictionary from database"""

        configuration = cls.session.execute(cls.select_conf_stmt,
                                            (dictionary_name,))

        acc_rows = cls.session.execute(cls.select_stmt,
                                       (True, dictionary_name))
        rej_rows = cls.session.execute(cls.select_stmt,
                                       (False, dictionary_name))

        if not configuration:
            return None
        else:
            return Dictionary.FromCassandra(dictionary_name,
                                            configuration,
                                            acc_rows,
                                            rej_rows)
        # if not acc_rows and not rej_rows:
        #    return None
        # else:
        #    return Dictionary.ByCassandraRows(dictionary_name,
        #                                      acc_rows,
        #                                      rej_rows)

    @classmethod
    def New(cls, dictionary_name):
        name = dictionary_name
        accepted_phrases = []
        rejected_phrases = []
        return cls(name, accepted_phrases, rejected_phrases)

    @classmethod
    def FromCassandra(cls, dictionary_name, configuration,
                      acc_rows, rej_rows):

        dictionary = Dictionary.New(dictionary_name)

        for result in configuration:
            source = result.source
            features = result.features
            dictionary.add_configuration(source, features)

        return dictionary

    @classmethod
    def ByCassandraRows(cls, dictionary_name, acc_rows, rej_rows):
        name = dictionary_name
        accepted_phrases = Phrase.ByCassandraRows(acc_rows)
        rejected_phrases = Phrase.ByCassandraRows(rej_rows)
        return cls(name, accepted_phrases, rejected_phrases)

    def add_configuration(self, source, features, ngrams, dfs):
        """Add source to container and map features"""
        self.sources.append(source)
        self.features[source] = features
        self.ngrams = ngrams
        self.dfs = dfs

    def print(self):
        print("Dictionary Name: " + self.name)
        for phrase in self.accepted_phrases:
            phrase.print()

    def insert_phrase(self, phrase):
        self.session.execute(self.insert_stmt,
                             (phrase.state, self.name,
                              phrase.phrase, phrase.similars))

    def all_phrases(self):
        phrases = []
        for phrase in self.accepted_phrases:
            phrases.append(phrase.phrase)

        for phrase in self.rejected_phrases:
            phrases.append(phrase.phrase)

        return phrases
