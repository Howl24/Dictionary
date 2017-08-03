from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect("general")

cmd = """
      INSERT INTO dictionary_phrases
      (dict_name, phrase, quantity, representative, source, state)
      VALUES
      ('test', 'excel intermedio', 510, 'excel intermedio', 'new_btpucp', False);
      """

session.execute(cmd);
