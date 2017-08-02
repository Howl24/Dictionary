from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
from cassandra.query import BoundStatement
import dictionary


class Offer:
    session = None
    keyspace = ""
    offers_table = "new_offers"
    select_stmt = None
    select_all_stmt = None

    def __init__(self, year=0, month=0, id="",
                 features={}, careers=set(), skills={}):
        self.year = year
        self.month = month
        self.id = id
        self.features = features
        self.careers = careers
        self.skills = skills

    @classmethod
    def ConnectToDatabase(cls, cluster):
        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable as e:
            print("Ningun servicio de cassandra esta disponible.")
            print("Inicie un servicio con el comando " +
                  "\"sudo cassandra -R \"")
            print()
            return dictionary.UNSUCCESSFUL_OPERATION

        return dictionary.SUCCESSFUL_OPERATION

    @classmethod
    def SetKeyspace(cls, keyspace):
        cls.keyspace = keyspace
        try:
            cls.session.set_keyspace(cls.keyspace)
        except InvalidRequest:
            print("El keyspace no existe")
            print()
            return dictionary.UNSUCCESSFUL_OPERATION

        cls.PrepareStatements()
        return dictionary.SUCCESSFUL_OPERATION

    @classmethod
    def PrepareStatements(cls, keyspace=None):
        if keyspace:
            if cls.SetKeyspace(keyspace) == dictionary.UNSUCCESSFUL_OPERATION:
                return dictionary.UNSUCCESSFUL_OPERATION

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     year = ? AND
                     month = ? AND
                     id = ?;
                     """.format(cls.offers_table)

        cmd_select_all = """
                         SELECT * FROM {0}
                         """.format(cls.offers_table)

        try:
            cls.select_stmt = cls.session.prepare(cmd_select)
            prepared_stmt = cls.session.prepare(cmd_select_all)
            cls.select_all_stmt = BoundStatement(prepared_stmt, fetch_size=10)
        except InvalidRequest:
            print("Tabla no configurada")
            raise
            return dictionary.UNSUCCESSFUL_OPERATION

        return dictionary.SUCCESSFUL_OPERATION

    @classmethod
    def Select(cls, year, month, id):
        rows = cls.session.execute(cls.select_stmt,
                                   (year, month, id))

        if not rows:
            return None
        else:
            return Offer.ByCassandraRow(rows[0])

    @classmethod
    def ByCassandraRow(cls, row):
        return cls(row.year, row.month, row.id, row.careers, row.features)

    @classmethod
    def SelectAll(cls, keyspace):
        cls.SetKeyspace(keyspace)
        rows = cls.session.execute(cls.select_all_stmt)

        if not rows:
            return None
        else:
            return cls.ByCassandraRows(rows)

    @classmethod
    def SelectSince(cls, keyspace, date):
        year = date[0]
        month = date[1]
        cls.SetKeyspace(keyspace)
        rows = cls.session.execute(cls.select_all_stmt)

        if not rows:
            return None
        else:
            selected_rows = []
            for row in rows:
                if (row.year > year) or \
                    ((row.year == year) and (row.month >= month)):
                    selected_rows.append(row)
                        
            return cls.ByCassandraRows(selected_rows)

    @classmethod
    def ByCassandraRows(cls, rows):
        offers = []
        for row in rows:
            offer = cls(row.year, row.month, row.id, row.features, row.careers)
            offers.append(offer)

        return offers
