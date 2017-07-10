from cassandra.cluster import Cluster

class Dictionary:
    session = None
    keyspace = ""

    def __init__(self, name):
        self.name = name

    @classmethod
    def ConnectToDatabase(cls, keyspace="new_dictionary", cluster=None):
        cls.keyspace = keyspace

        if not cluster:
            cluster = Cluster()
        cls.session = cluster.connect(cls.keyspace);

    @classmethod
    def CreateTable(cls):
        if not cls.session:
            cls.ConnectToDatabase();

        cmd = """
               CREATE TABLE IF NOT EXISTS {0} (
               state boolean,
               name text,
               phrase text,
               similars set<text>,
               PRIMARY KEY ((state, name), phrase));
               """.format(cls.keyspace)

        cls.session.execute(cmd)
        try:
            pass
        except:
            print("No se pudo crear la tabla de diccionarios")
            return False

        return True
        
    @classmethod
    def FromDatabase(cls, name):
        cmd = """
              SELECT * FROM new_dictionaries WHERE
              name = %s
              """

        rows = cls.session.execute(cmd, [name])


if __name__ == "__main__":
    Dictionary.ConnectToDatabase()
    Dictionary.CreateTable()
