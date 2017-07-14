from cassandra.cluster import NoHostAvailable
import dictionary


class Dictionary:
    session = None
    keyspace = "general"
    table_name = "new_dictionary"
    insert_stmt = None
    select_stmt = None
    delete_stmt = None

    def __init__(self, state, name, phrase, similars):
        self.state = state
        self.name = name
        self.phrase = phrase
        self.similars = similars

    # Pre  :
    #   - Cluster instance
    # Post :
    #   - Class session instantiated
    @classmethod
    def ConnectToDatabase(cls, cluster):
        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable as e:
            print("Ningun servicio de cassandra esta disponible.")
            print("Inicie un servicio con el comando " +
                  "\"sudo cassandra -R\"")
            print()
            return dictionary.UNSUCCESFUL_OPERATION

        return dictionary.SUCCESFUL_OPERATION

    # Pre:
    #   - Class session instance
    # Post:
    #   - Class PreparedStatements instantiated
    @classmethod
    def BuildPreparedStatements(cls):
        cmd_insert = """
                     INSERT INTO {0}
                     (state, name, phrase, similars)
                     VALUES
                     (?, ?, ?, ?);
                     """.format(cls.table_name)

        cls.insert_stmt = cls.session.prepare(cmd_insert)

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     state = ? AND
                     name = ?;
                     """.format(cls.table_name)

        cls.select_stmt = cls.session.prepare(cmd_select)

        cmd_delete = """
                     DELETE FROM {0} WHERE
                     state = ? AND
                     name = ?;
                     """.format(cls.table_name)

        cls.delete_stmt = cls.session.prepare(cmd_delete)

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

        try:
            cls.session.execute(cmd)
        except:
            # print("No se pudo crear la tabla de diccionarios")
            # print(Exception.errors)
            return dictionary.UNSUCCESFUL_OPERATION

        print("La tabla de diccionarios se creó correctamente")
        return dictionary.SUCCESFUL_OPERATION
